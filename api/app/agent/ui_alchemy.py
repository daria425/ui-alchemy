# RUN WITH  python -m app.agent.ui_alchemy
from langgraph.graph import StateGraph, END, START
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.utils.file_utils import load_file
from app.utils.graph_utils import display_graph
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient
from app.agent.config import (AGENT_INSTRUCTIONS_PATH, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, MONGO_URI)
from app.agent.tools import ui_gen_function
from app.agent.state import State

client= MongoClient(MONGO_URI)
db = client["ui_alchemy"]
print(f"Initializing LLM with endpoint: {AZURE_OPENAI_ENDPOINT}")
llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2025-01-01-preview",
)
checkpointer=MongoDBSaver(client=client, db_name=db.name, checkpoint_collection_name="sessions" )


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
    system_prompt = load_file(AGENT_INSTRUCTIONS_PATH)
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
        "valid_request": response.content,
    }

def select_libraries(state: State):
    """Select the appropriate libraries for the component based on the user description"""
    print("Selecting libraries...")
    context = "\nContext from follow up questions:\n"
    for exchange in state["conversation_history"]:
        if isinstance(exchange, list) and len(exchange) == 2:
            ai_msg, human_msg = exchange
            context += f"Question: {ai_msg.content}\nAnswer: {human_msg.content}\n\n"
    system_prompt=f"""
Act as a UI designer and experienced Frontend developer. Based on this UI component description {state['component_request']}
And follow-up context:\n{context}"
    Determine the most appropriate React library/libraries to implement this component.
    Consider these options and combinations. These are the only libraries you can use:
   
    1. Material UI (@mui/material) - Standard components with Google Material Design
    2. Chakra UI - Accessible and customizable component system
    3. React Bootstrap - Bootstrap for React applications
    4. Ant Design - Enterprise-grade UI components
    5. Tailwind CSS - Utility-first CSS framework (pair with headless UI if needed)
    6. Specialty libraries when needed:
       - For charts/graphs: recharts, visx, or chart.js
       - For complex tables: react-table or tanstack table
       - For animations: framer-motion or react-spring
       - For forms: react-hook-form, formik, or yup for validation
       - For date handling: date-fns or moment.js

    Keep your analysis focused on the component's requirements and the libraries' capabilities.
    Your response must adhere to the following guidelines:
    1. Be concise and avoid unnecessary details. 
    2. Keep your response to 1-3 sentences.
    3. Provide a clear, deterministic list of recommended libraries.
    4. Avoid vague or ambiguous language.
    5. Clearly mention the names of the packages to install from npm.
"""
    messages=[SystemMessage(content=system_prompt)]
    response=llm.invoke(messages)
    return {
        "ui_guidance": response.content,
    }

def generate_code(state: State):
    """Generate code for the component"""
    print("Generating code...")
    system_prompt = load_file(AGENT_INSTRUCTIONS_PATH)    
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
        user_prompt = f"""Generate a component based on this description:
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
    system_prompt = load_file(AGENT_INSTRUCTIONS_PATH)
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
    if "yes" in state["valid_request"].lower():
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
builder.add_node("select_libraries", select_libraries)
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
        "generate_code": "select_libraries",
        "ask_for_clarification": "ask_for_clarification",
    },
)
builder.add_conditional_edges(
    "ask_for_clarification",
    route_message,
    {
        "generate_code": "select_libraries",
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
builder.add_edge("select_libraries", "prune_conversation_history")
builder.add_edge("prune_conversation_history", "generate_code")
builder.add_edge("generate_code", "validate_code")
builder.add_edge("handle_validation_error", "get_final_response")
graph=builder.compile(checkpointer=checkpointer, interrupt_after=["ask_for_clarification"])
display_graph(graph, "graph.png")



