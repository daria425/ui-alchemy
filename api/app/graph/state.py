from typing import TypedDict, Union, Annotated, List
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
    valid_request:str
    conversation_history: Annotated[
        List, manage_conversation_history
    ]  # whenever a node returns an update for this field, instead of directly replacing its value, call the manage_conversation_history function to determine how to merge the old state with the update
    component_data: dict[str, str]
    status: str
