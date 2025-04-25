from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional, List

class ComponentRequest(BaseModel):
    description: str

class UserMessage(BaseModel):
    message: str

class MessageItem(BaseModel):
    role: str
    content: str
    model_config=ConfigDict(extra="allow")


class ComponentResponse(BaseModel):
    session_id: str
    status: str
    message: str
    requires_input: bool = False
    component_data: Optional[Dict[str, str]] = None
    messages: Optional[List[MessageItem]] = None