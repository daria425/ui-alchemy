from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from pydantic import BaseModel, Field
from typing import Dict, Optional
from agents.langgraph_api import graph
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
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
        "llm_response": "",
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
        session_id=session_id,
        status=result["status"],
        message=result["ai_message"],

    )





