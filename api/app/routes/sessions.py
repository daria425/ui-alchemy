from fastapi import APIRouter, HTTPException, Depends
from app.models.component_generation import ComponentRequest, UserMessage, ComponentResponse
from uuid import uuid4
from app.agent.ui_alchemy import initialize_ui_alchemy
from app.agent.state import process_user_input
from app.dependencies.auth import get_uid
from app.dependencies.database import get_session_collection
from app.db.database_services import SessionDatabaseService
from app.utils.logger import logger
from datetime import datetime, timezone
router=APIRouter(prefix="/ui-alchemy/api/sessions")

def get_ui_alchemy()->tuple:
    """
    Dependency to get the UI Alchemy instance
    """
    graph, checkpointer=initialize_ui_alchemy()
    return graph, checkpointer

@router.get("/")
def get_user_sessions(uid:str=Depends(get_uid), session_collection:SessionDatabaseService=Depends(get_session_collection)):
    """
    Get all sessions for the user
    """
    try:
        sessions=session_collection.get_user_sessions(uid)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/", response_model=ComponentResponse)
def create_new_session(request: ComponentRequest, ui_alchemy:tuple=Depends(get_ui_alchemy), uid:str=Depends(get_uid)):
    """
    Start a new component generation session
    """
    graph=ui_alchemy[0]
    created_at=datetime.now(timezone.utc)
    try:
        metadata = {
            "created_at": created_at,
            "updated_at": created_at,
            "title": request.description[:50] + ("..." if len(request.description) > 50 else ""),
        }
        session_id = str(uuid4())
        initial_state = {
            "component_request": request.description,
            "valid_request": "",
            "ui_guidance":"",
            "conversation_history": [],
            "user_input": "",
            "force_generate": False,
            "validation_feedback": "",
            "validation_attempts": 0,
            "status": "",
            "ai_message": ""
        }
        config={"configurable":{"thread_id":session_id, "uid":uid}, "metadata":metadata}
        result=graph.invoke(initial_state, config)
        print(result)
        return ComponentResponse(
            session_id=session_id, # returned to client, used in next request
            status=result["status"],
            message=result["ai_message"],
            component_data=result.get("component_data", None),
            requires_input=result.get("status")=="awaiting_user_input",
            conversation_history=result.get("conversation_history", []),
            )
    except Exception as e:
        logger.error(f"❌ Error creating new session: {e} ❌")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/messages")
def add_message(session_id:str, message:UserMessage, ui_alchemy:tuple=Depends(get_ui_alchemy), session_collection:SessionDatabaseService=Depends(get_session_collection)):
    """
    Continue an existing session with an additional message
    """
    graph, checkpointer=ui_alchemy
    try:
        config={"configurable":{"thread_id":session_id}}
        if not checkpointer.get(config):
            raise HTTPException(status_code=404, detail="Session not found")
        saved_config=checkpointer.get(config)
        current_state=saved_config["channel_values"]
        updated_state=process_user_input(current_state, message.message)
        result=graph.invoke(updated_state, config)
        session_collection.update_session_metadata(session_id)
        return ComponentResponse(
            session_id=session_id, # returned to client, used in next request
            status=result["status"],
            message=result["ai_message"],
        requires_input=result.get("status")=="awaiting_user_input",
            component_data=None if result.get("status")=="awaiting_user_input" else result.get("component_data", None),
            conversation_history=result.get("conversation_history", []),
        )
    except Exception as e:
        logger.error(f"❌ Error adding message: {e} ❌")
        raise HTTPException(status_code=500, detail=str(e))

# TODO: Add route to get user sessions
