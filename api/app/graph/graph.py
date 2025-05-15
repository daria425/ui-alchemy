from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.graph.state import State
from app.utils.file_utils import load_file
from app.graph.tools import structured_ui_gen_tool
from pprint import pprint
import os, json
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
system_instruction_file_path=os.path.join(BASE_DIR, "system_instructions.txt")

ui_gen_llm=ChatAnthropic(model="claude-3-7-sonnet-latest", temperature=0.5)
def understand_requirements(state: State):
    print("Understanding requirements...")
    system_instructions=load_file(system_instruction_file_path)
    prompt = f"""Act as a magical UI requirements analyst for a visual alchemy engine.

You will evaluate the user's component request: "{state['component_request']}"

1. Decide if the request contains **enough design detail** (e.g., colors, labels, layout, effects, structure) to generate a **complete, styled, and enchanted UI component**.
2. If YES, respond only with **"yes"**.
3. If NO, respond only with **"no"**.

Only say "yes" if the user has provided sufficient magical or visual ingredients to create a full component — such as visual style, behavior, structure, effects, or mood.

Examples:

User Prompt: "Create a button"  
Assistant: no

User Prompt: "Create a glowing, lavender-themed 'Save' button that pulses on hover"  
Assistant: yes

User Prompt: "Make a chart"  
Assistant: no

User Prompt: "Build a donut chart showing task completion at 80%, with a neon pink ring and floating percentage label in the center"  
Assistant: yes

User Prompt: "Create a dashboard widget for analytics"  
Assistant: no

User Prompt: "Design a user profile card with a circular profile picture, soft gradient background, and shimmering border"  
Assistant: yes
"""
    system_message = SystemMessage(content=system_instructions)
    human_message = HumanMessage(content=prompt)
    ai_message=ui_gen_llm.invoke([system_message, human_message])
    return {
        "valid_request": ai_message.content,
    }

def improve_human_prompt(state:State):
    print("Requirements not clear, improving prompt...")
    prompt=f"""
Act as a Prompt Alchemist. Your task is to transmute the user's vague or incomplete request into a richly detailed incantation that can be used to conjure a complete and styled UI component.

The user's original request is: "{state['component_request']}"

1. Examine the prompt for missing magical ingredients — such as visual details (colors, layout, size, labels, structure, animations, themes).
2. Suggest additions that would help the design be fully realized.
3. Rewrite the user's prompt to include these enhancements in a detailed, short paragraph.
4. The purpose is for an LLM to generate a beautiful, magical component, so be creative.
5. Include animations and effects, gradients or fun colors, and any other details that would make the component visually stunning.

Respond with only the improved prompt in this format:
{{"improved_prompt": "Revised prompt here"}}
"""
    human_msg=HumanMessage(content=prompt)
    system_msg=SystemMessage(content="You are a Prompt Alchemist, enhancing user prompts for UI generation.")
    ai_msg=ui_gen_llm.invoke([system_msg, human_msg])
    improved_prompt=json.loads(ai_msg.content)
    print("Improved prompt:", improved_prompt)
    return {
        "component_request": improved_prompt["improved_prompt"],
    }
    
def generate_code(state: State):
    """Generate code for the component"""
    print("Generating code...")
    user_prompt = f"""Generate a component based on this description:
    "{state['component_request']}"
    Create high-quality, production-ready code that matches all specifications.
    Use the UI gen tool to return the structured data.
    IMPORTANT: When using the tool, ENSURE you provide the code
    """
    system_prompt=load_file(system_instruction_file_path)
    messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    llm_with_tools = ui_gen_llm.bind_tools([structured_ui_gen_tool])
    response = llm_with_tools.invoke(messages)
    print("Response from LLM:", response.content)
    tool_calls = response.tool_calls
    if tool_calls:
        # Extract the tool call data
        print("Tool calls:", tool_calls)
        tool_call = next(
            (call for call in tool_calls), None
        )
        code = tool_call["args"]["code"]
        print("Generated code:", code)
        return {
            "component_data": {
                "code": code,
            },
        }

def route_validation(state: State):
    print("Routing to validation...")
    if "yes" in state["valid_request"]:
        return "generate_code"
    else:
        return "improve_human_prompt"

    
    
    
builder=StateGraph(State)
builder.add_node("understand_requirements", understand_requirements)    
builder.add_node("improve_human_prompt", improve_human_prompt)
builder.add_node("generate_code", generate_code)

builder.add_edge(START, "understand_requirements")
builder.add_conditional_edges("understand_requirements", route_validation, {
    "improve_human_prompt": "improve_human_prompt",
    "generate_code": "generate_code",
})
builder.add_edge("improve_human_prompt", "understand_requirements")
builder.add_edge("generate_code", END)

graph=builder.compile()

component_request="Create a button"
initial_state={
    "component_request": component_request,
    "valid_request": "",
    "component_data": {},
    "status": "",
}

final_state=graph.invoke(initial_state)
print("Final State:")
pprint(final_state)