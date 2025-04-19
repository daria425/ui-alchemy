import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import TypedDict, List, Annotated, Union
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END, START
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from utils.file_utils import load_file
from pydantic import BaseModel
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

instruction_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "agent_instructions.txt"
)

load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MONGO_URI = os.getenv("MONGO_URI")
client= MongoClient(MONGO_URI)
db = client["ui_alchemy"]
print(f"Initializing LLM with endpoint: {AZURE_OPENAI_ENDPOINT}")
llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2025-01-01-preview",
)
checkpointer=MongoDBSaver(client=client, db_name=db.name, checkpoint_collection_name="sessions" )


# Create our function tool
@tool
def ui_gen_function(install_script: str, imports: str, code: str, description: str):
    """
    Function to generate a Material UI component
    :param install_script: The script to install the required packages
    :param imports: The imports required for the component
    :param code: The code for the component
    :param description: The description of the component
    :return: A dictionary containing the install script, imports, code, and description
    """
    return {
        "install_script": install_script,
        "imports": imports,
        "code": code,
        "description": description,
    }


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
    llm_response: str
    conversation_history: Annotated[
        List, manage_conversation_history
    ]  # whenever a node returns an update for this field, instead of directly replacing its value, call the manage_conversation_history function to determine how to merge the old state with the update
    user_input: str
    component_data: dict[str, str]
    force_generate: bool
    validation_feedback:str
    validation_attempts: int
    status: str
    ai_message: str

def process_user_input(state: State, user_message:str):
    """
    Add users response to clarification questions to the conversation history
    """
    component_request=state.get("component_request", "")
    ai_message=state.get("ai_message", "")
    conversation_history=state.get("conversation_history", [])
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
        "status": ""  # Clear awaiting_user_input status
    }


def prune_conversation_history(state: State):
    """
    Prune the conversation history to keep only the last 3 exchanges
    """
    # Get the existing conversation history
    existing_history = state.get("conversation_history", [])
    # Keep only the last 3 exchanges
    if len(existing_history) <= 3:
        return {}
    return {
        "conversation_history": {
            "action": "prune"
            # later add keep_count
        }
    }


def understand_requirements(state: State):
    print("Understanding requirements...")
    system_prompt = load_file(instruction_file_path)
    prompt = f"""Act as a requirements analyst. 
                    Given the following user request: "{state['component_request']}"
                    1. Determine if there is enough detail to generate working component code (e.g., styles, colors, labels, layout specifics).
                    2. If YES, respond only with "yes".
                    3. If NO, respond only with "no".

                    Your decision should be based on whether the user has provided enough design-specific information (like color scheme, data structure, size, layout, etc.) to create a visually complete and functional component.
                    Examples:
                    User Prompt: "Create a button"
                    Assistant: no

                    User Prompt: "Build a blue-themed submit button with rounded corners that says 'Save'"
                    Assistant: yes

                    User Prompt: "Make a chart"
                    Assistant: no

                    User Prompt: "Build a donut chart showing task completion at 80%. Use pink and white as primary colors."
                    Assistant: yes

                    User Prompt: "Create a dashboard widget for analytics"
                    Assistant: no

                    User Prompt: "Create a card component showing a user's profile picture, name, and email, with a light gray background."
                    Assistant: yes
                    """
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return {
        "llm_response": response.content,
    }



def generate_code(state: State):
    """Generate the MUI code for the component"""
    print("Generating code...")
    system_prompt = load_file(instruction_file_path)    
    context = "\nContext from follow up questions:\n"
    for exchange in state["conversation_history"]:
        if isinstance(exchange, list) and len(exchange) == 2:
            ai_msg, human_msg = exchange
            context += f"Question: {ai_msg.content}\nAnswer: {human_msg.content}\n\n"
    if state.get("validation_feedback"):
        system_prompt=f"""
This component has recieved the following feedback from a code reviewer:
## FEEDBACK ##
{state['validation_feedback']}
## END FEEDBACK ##
## COMPONENT ##
Install script:
{state['component_data']['install_script']}
Component:
{state['component_data']['imports']}
{state['component_data']['code']}
## END COMPONENT ##
Fix the code to address these issues and ensure it meets the user's request:
{state['component_request']}.
"""
        messages=[
        SystemMessage(content=system_prompt)]
    else:
        user_prompt = f"""Generate a Material UI component based on this description:
            "{state['component_request']}"
            {context}
            Create high-quality, production-ready code that matches all specifications.
            Use the ui_gen_function tool to return the structured data.
            """
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    llm_with_tools = llm.bind_tools([ui_gen_function], tool_choice="required")
    response = llm_with_tools.invoke(messages)
    tool_calls = response.tool_calls
    if tool_calls:
        # Extract the tool call data
        tool_call = next(
            (call for call in tool_calls if call["name"] == "ui_gen_function"), None
        )
        install_script = tool_call["args"]["install_script"]
        imports = tool_call["args"]["imports"]
        code = tool_call["args"]["code"]
        description = tool_call["args"]["description"]
        return {
            "component_data": {
                "install_script": install_script,
                "imports": imports,
                "code": code,
                "description": description,
            },
        }
    

def validate_code(state:State):
    print("Validating code...")
    component_data= state.get("component_data", {})
    validation_attempts= state.get("validation_attempts", 0)
    system_prompt=f"""
Act as a code reviewer skilled in Frontend development. Your task is to review the following code:
## INSTALL SCRIPT ##
{component_data.get('install_script', '')}

## IMPORTS ##
{component_data.get('imports', '')}

## CODE ##
{component_data.get('code', '')}
Ensure that:
1. It is syntactically correct and adheres to best practices.
2. It is well-structured and easy to read.
3.It includes a default export called MUI Component.
4. The component within the code is fully self contained, can be rendered alone and does not rely on any external variables or data.
5. The component fits the following request: {state['component_request']}
If the code meets all the above criteria, respond with "yes" only. 
If it does not, respond with "no" and provide a brief explanation of the issues, clearly explaining how to fix."""
    messages=[SystemMessage(content=system_prompt)]
    print(f"--- Code Review In Progress ---(Attempt {validation_attempts}/3)")
    response=llm.invoke(messages)
    validation_attempts+=1
    return {
        "validation_feedback": response.content,
        "validation_attempts": validation_attempts,
    }


def ask_for_clarification(state: State):
    """
    Generate clarifying questions and wait for user input
    """
    # Get current component request
    print("Clarification required!")
    component_request = state.get("component_request", "")
    # Generate follow-up questions using the LLM
    system_prompt = load_file(instruction_file_path)
    prompt = f"""
Act as a UI designer. Ask a series of follow up questions to gather more information about the request to generate the following component: "{component_request}"
1. Ask about the specific design elements needed (e.g., colors, styles, layout).
2. Inquire about the functionality and behavior of the component (e.g., click handlers, data binding).
3. Clarify the context in which the component will be used (e.g., part of a larger application, standalone).
4. Be conscise. No yapping.
"""
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    clarification_questions = response.content
    return {
        "ai_message": clarification_questions,
        "status":"awaiting_user_input"
    }

def handle_validation_error(state: State):
    """
    Prevent infinite loops by limiting the number of validation attempts and returning the response after 3 attemps
    """
    print("Validation failed after 3 attempts.")
    return {
        "status":"validation_failure"
    }

def get_final_response(state: State):
    component_result = state.get("component_data", {})
    if component_result:
        output = "\n".join(component_result.values())
        print("\n--- Generated Component ---")
        return {
            "status":"success"
        }


def route_message(state: State):
    """
    Route the message to the appropriate function based on the state
    """
    if state.get("force_generate", False):
        print("Force generate is TRUE - routing to generate_code")
        return "generate_code"
    if "yes" in state["llm_response"].lower():
        print("Requirements understood - routing to generate_code")
        return "generate_code"
    else:
        return "ask_for_clarification"
    
def route_validation(state:State):
    """
    Route the message to the appropriate function based on the state
    """
    validation_attempts=state.get("validation_attempts", 0)
    if validation_attempts >= 3 and "yes" not in state["validation_feedback"].lower():
        print("Validation failed after 3 attempts, routing to handle_validation_error")
        return "handle_validation_error"
    if "yes" in state["validation_feedback"].lower():
        print("Code Review passed, routing to get_final_response")
        return "get_final_response"
    else:
        print("Code Review failed, routing to generate_code")
        return "generate_code"


builder = StateGraph(State)
builder.add_node("understand_requirements", understand_requirements)
builder.add_node("generate_code", generate_code)
builder.add_node("get_final_response", get_final_response)
builder.add_node("ask_for_clarification", ask_for_clarification)
builder.add_node("prune_conversation_history", prune_conversation_history)
builder.add_node("validate_code", validate_code)
builder.add_node("handle_validation_error", handle_validation_error)


builder.add_edge(START, "understand_requirements")
builder.add_edge("get_final_response", END)

builder.add_conditional_edges(
    "understand_requirements",
    route_message,
    {
        "generate_code": "prune_conversation_history",
        "ask_for_clarification": "ask_for_clarification",
    },
)
builder.add_conditional_edges(
    "ask_for_clarification",
    route_message,
    {
        "generate_code": "prune_conversation_history",
        "ask_for_clarification": END
    },
)
builder.add_conditional_edges(
    "validate_code", route_validation, {
        "get_final_response": "get_final_response",
        "generate_code":"generate_code",
        "handle_validation_error": "handle_validation_error",
    }
)
builder.add_edge("generate_code", "validate_code")
builder.add_edge("prune_conversation_history", "generate_code")
builder.add_edge("handle_validation_error", "get_final_response")
graph=builder.compile(checkpointer=checkpointer, interrupt_after=["ask_for_clarification"])




