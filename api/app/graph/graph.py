from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.graph.state import State
from app.utils.file_utils import load_file
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

The user's original spell is: "{state['component_request']}"

1. Examine the prompt for missing magical ingredients — such as visual details (colors, layout, size, labels, structure, animations, themes).
2. Suggest additions that would help the design be fully realized.
3. Rewrite the user's prompt to include these enhancements in a single, well-structured line.

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
    
def route_validation(state: State):
    print("Routing to validation...")
    if "yes" in state["valid_request"]:
        return END
    else:
        return "improve_human_prompt"

    
    
    
builder=StateGraph(State)
builder.add_node("understand_requirements", understand_requirements)    
builder.add_node("improve_human_prompt", improve_human_prompt)

builder.add_edge(START, "understand_requirements")
builder.add_conditional_edges("understand_requirements", route_validation, {
    "improve_human_prompt": "improve_human_prompt",
    END: END
})
builder.add_edge("improve_human_prompt", "understand_requirements")

graph=builder.compile()

component_request="Create a button"
initial_state={
    "component_request": component_request,
    "valid_request": "",
    "conversation_history": [],
    "user_input": "",
    "ui_guidance": "",
    "component_data": {},
    "force_generate": False,
    "validation_feedback": "",
    "validation_attempts": 0,
    "status": "",
    "ai_message": "",
    "chat_messages": []
}

final_state=graph.invoke(initial_state)
print("Final State:")
pprint(final_state)