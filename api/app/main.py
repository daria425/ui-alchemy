from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from pydantic import BaseModel
from typing import Dict, Optional
from app.agent.ui_alchemy import graph, checkpointer
from app.agent.state import process_user_input
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComponentRequest(BaseModel):
    description: str

class UserMessage(BaseModel):
    message: str

class ComponentResponse(BaseModel):
    session_id: str
    status: str
    message: str
    requires_input: bool = False
    component_data: Optional[Dict[str, str]] = None

@app.post("/ui-alchemy/api/sessions", response_model=ComponentResponse)
def create_new_session(request:ComponentRequest):
    """
    Start a new component generation session
    """
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


@app.post("/ui-alchemy/api/sessions/messages", response_model=ComponentResponse)
def add_message(session_id:str, message:UserMessage):
    """
    Continue an existing session with an additional message
    """
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
        component_data=result.get("component_data", None)
    )




