from fastapi import APIRouter, HTTPException, Depends
from app.models.component_generation import ComponentRequest, UserMessage, ComponentResponse
from uuid import uuid4
from app.agent.ui_alchemy import initialize_ui_alchemy
from app.agent.state import process_user_input
router=APIRouter(prefix="/ui-alchemy/api/sessions")

def get_ui_alchemy()->tuple:
    """
    Dependency to get the UI Alchemy instance
    """
    graph, checkpointer=initialize_ui_alchemy()
    return graph, checkpointer

@router.post("/", response_model=ComponentResponse)
def create_new_session(request: ComponentRequest, ui_alchemy:tuple=Depends(get_ui_alchemy)):
    """
    Start a new component generation session
    """
    graph=ui_alchemy[0]
    try:
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
def add_message(session_id:str, message:UserMessage, ui_alchemy:tuple=Depends(get_ui_alchemy)):
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
