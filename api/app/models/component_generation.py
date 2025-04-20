from pydantic import BaseModel
from typing import Dict, Optional

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