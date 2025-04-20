from fastapi import APIRouter, HTTPException
from app.models.component_generation import ComponentRequest, UserMessage, ComponentResponse
from uuid import uuid
from app.agent.ui_alchemy import graph, checkpointer
from app.agent.state import process_user_input
router=APIRouter(prefix="/ui-alchemy/api/sessions")


@router.post("/", response_model=ComponentResponse)
def create_new_session(request: ComponentRequest):
    """
    Start a new component generation session
    """
    try:
        session_id=str(uuid.uuid4())
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
        config={"configurable":{"thread_id":session_id}}
        result=graph.invoke(initial_state, config)
        print(result)
        return ComponentResponse(
            session_id=session_id, # returned to client, used in next request
            status=result["status"],
            message=result["ai_message"],
            component_data=result.get("component_data", None),
            requires_input=result.get("status")=="awaiting_user_input"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/messages")
def add_message(session_id:str, message:UserMessage):
    """
    Continue an existing session with an additional message
    """
    try:
        config={"configurable":{"thread_id":session_id}}
        if not checkpointer.get(config):
            raise HTTPException(status_code=404, detail="Session not found")
        saved_config=checkpointer.get(config)
        current_state=saved_config["channel_values"]
        updated_state=process_user_input(current_state, message.message)
        result=graph.invoke(updated_state, config)
        print(result)
        return ComponentResponse(
            session_id=session_id, # returned to client, used in next request
            status=result["status"],
            message=result["ai_message"],
        requires_input=result.get("status")=="awaiting_user_input",
            component_data=None if result.get("status")=="awaiting_user_input" else result.get("component_data", None),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
