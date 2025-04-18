import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END, START
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage,SystemMessage
from utils.graph_utils import display_graph
from utils.file_utils import load_file

instruction_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "agent_instructions.txt"
)

load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
print(f"Initializing LLM with endpoint: {AZURE_OPENAI_ENDPOINT}")
llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2025-01-01-preview",
)
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




class State(TypedDict):
    component_request:str
    llm_response:str
    conversation_history:List[str]
    user_input:str
    component_data:dict[str, str]
    force_generate:bool

def understand_requirements(state: State):
    system_prompt=load_file(instruction_file_path)
    prompt=f"""Act as a requirements analyst. 
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
    messages=[SystemMessage(content=system_prompt),HumanMessage(content=prompt)]
    response=llm.invoke(messages)
    return {
        "llm_response": response.content,
    }


def generate_code(state:State):
    """Generate the MUI code for the component"""
    print("State in generate code", state)
    system_prompt=load_file(instruction_file_path)
    context="\nContext from follow up questions:\n"
    for exchange in state["conversation_history"]:
        if isinstance(exchange, list) and len(exchange) == 2:
            ai_msg, human_msg= exchange
            context += f"Question: {ai_msg.content}\nAnswer: {human_msg.content}\n\n"
    user_prompt = f"""Generate a Material UI component based on this description:
    "{state['component_request']}"
    {context}
    Create high-quality, production-ready code that matches all specifications.
    Use the ui_gen_function tool to return the structured data.
    """
    messages=[
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    llm_with_tools=llm.bind_tools([ui_gen_function], tool_choice="required")
    response=llm_with_tools.invoke(messages)
    tool_calls=response.tool_calls
    if tool_calls:
        # Extract the tool call data
        tool_call = next((call for call in tool_calls if call['name'] == "ui_gen_function"), None)
        install_script = tool_call['args']["install_script"]
        imports = tool_call['args']["imports"]
        code = tool_call['args']["code"]
        description = tool_call['args']["description"]
        return {
            "component_data": {
                "install_script": install_script,
                "imports": imports,
                "code": code,
                "description": description,
            },
        }






def ask_for_clarification(state:State):
    """
    Generate clarifying questions and wait for user input
    """
    # Get current component request
    component_request = state.get("component_request", "")
    # Generate follow-up questions using the LLM
    system_prompt=load_file(instruction_file_path)
    prompt=f"""
Act as a UI designer. Ask a series of follow up questions to gather more information about the request to generate the following component: "{component_request}"
1. Ask about the specific design elements needed (e.g., colors, styles, layout).
2. Inquire about the functionality and behavior of the component (e.g., click handlers, data binding).
3. Clarify the context in which the component will be used (e.g., part of a larger application, standalone).
4. Be conscise. No yapping.
"""
    messages=[SystemMessage(content=system_prompt),HumanMessage(content=prompt)]
    response=llm.invoke(messages)
    clarification_questions=response.content
    print("\n--- UI Alchemy Needs More Information ---")
    print(clarification_questions)

    user_input = input("\nYour response (or type 'generate' to proceed anyway): ")
    conversation_history = state.get("conversation_history", [])
    conversation_history.append([AIMessage(content=clarification_questions), HumanMessage(content=user_input)])
    
    force_generate = user_input.lower() == "generate"
    if not force_generate:
        updated_request=f"{component_request} {user_input}"
    else:
        updated_request=component_request
    return {
        "conversation_history": conversation_history,
        "user_input": user_input,
        "component_request": updated_request,
        "force_generate": force_generate,
    }


    
def get_final_response(state:State):
    print("State in get_final_response", state)
    component_result=state.get("component_data", {})
    if component_result:
        output="\n".join(component_result.values())
        print("\n--- Generated Component ---")
        print(output)
    

def route_message(state: State):
    """
    Route the message to the appropriate function based on the state
    """
    print("Current state in route_message:", state)
    if state.get("force_generate", False):
        print("Force generate is TRUE - routing to generate_code")
        return "generate_code"
    if "yes" in state["llm_response"].lower():
        return "generate_code"
    else:
        return "ask_for_clarification"

builder=StateGraph(State)
builder.add_node("understand_requirements", understand_requirements)
builder.add_node("generate_code", generate_code)
builder.add_node("get_final_response", get_final_response)
builder.add_node("ask_for_clarification", ask_for_clarification)

builder.add_edge(START, "understand_requirements")
builder.add_edge("get_final_response", END)

builder.add_conditional_edges(
    "understand_requirements",route_message, {
        "generate_code": "generate_code",
        "ask_for_clarification": "ask_for_clarification",
    } 
)
builder.add_conditional_edges(
    "ask_for_clarification", route_message, {
        "generate_code": "generate_code",
        "ask_for_clarification": "understand_requirements",
    }
)
builder.add_edge("generate_code", "get_final_response")
graph=builder.compile()
display_graph(graph, "graph.png")
# Example of running the graph
def run_ui_alchemy():
    user_prompt = input("Describe the UI component you want to create: ")
    
    # Initialize state with the user's component request
    initial_state = {
        "component_request": user_prompt,
        "llm_response": "",
        "conversation_history": [],
        "user_input": "", 
        "force_generate": False,
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    # Display the result
    if "component_data" in result:
        print("\n--- Generated Component ---")
        component = result["component_data"]
        print(f"Description: {component['description']}")
        print(f"Install Script: {component['install_script']}")
        print(f"Imports: {component['imports']}")
        print(f"Code: {component['code']}")

if __name__ == "__main__":
    run_ui_alchemy()