from typing import TypedDict, List, Annotated, Union
from langchain_core.messages import HumanMessage, AIMessage

def manage_conversation_history(existing: list, updates: Union[list, dict]):
    if isinstance(updates, list):
        # If updates is a list, append it to the existing conversation history
        return existing + updates
    elif isinstance(updates, dict) and updates.get("action"):
        keep_count = 3  # number of previous exchanges to keep, hardcoded for now
        if len(existing) <= keep_count:
            return existing
        return existing[-keep_count:]
    return existing

class State(TypedDict):
    component_request: str
    valid_request: str
    conversation_history: Annotated[
        List, manage_conversation_history
    ]  # whenever a node returns an update for this field, instead of directly replacing its value, call the manage_conversation_history function to determine how to merge the old state with the update
    user_input: str
    ui_guidance:str
    component_data: dict[str, str]
    force_generate: bool
    validation_feedback: str
    validation_attempts: int
    status: str
    ai_message: str
    
def process_user_input(state: dict, user_message: str):
    """
    Add users response to clarification questions to the conversation history
    """
    component_request = state.get("component_request", "")
    ai_message = state.get("ai_message", "")
    conversation_history = state.get("conversation_history", [])
    conversation_history.append(
        [AIMessage(content=ai_message), HumanMessage(content=user_message)]
    )
    
    # Check if user wants to force generate
    force_generate = user_message.lower() == "generate"
    
    if not force_generate:
        updated_request = f"{component_request} {user_message}"
    else:
        updated_request = component_request
        
    return {
        "conversation_history": conversation_history,
        "user_input": user_message,
        "component_request": updated_request,
        "force_generate": force_generate,
        "status": "",  # Clear awaiting_user_input status
        "ai_message": ""  # Also clear the AI message
    }