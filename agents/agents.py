import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.azure_ai_project_config import project_client
import time
from azure.ai.projects.models import FunctionTool, RequiredFunctionToolCall, SubmitToolOutputsAction
from utils.file_utils import load_file
from utils.logger import logger, shut_up_azure_logging
from dotenv import load_dotenv
load_dotenv()
shut_up_azure_logging()
UI_AGENT_ID=os.getenv("UI_AGENT_ID")
instruction_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_instructions.txt")
instructions=load_file(instruction_file_path)

def ui_gen_function(install_script:str, imports:str, code:str, description:str):
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
        "description": description
    }

function_tool = FunctionTool(
    functions=[ui_gen_function]
)

agent=project_client.agents.update_agent(agent_id=UI_AGENT_ID, instructions=instructions, tools=function_tool.definitions)


def run_agent(user_prompt:str):
        max_retries = 3
        retry_delay = 30  # seconds
        
        for attempt in range(max_retries):
            try:
                thread = project_client.agents.create_thread()  # Create a NEW thread
                thread_id = thread.id
                message = project_client.agents.create_message(
                    thread_id=thread_id,
                    role="user",
                    content=f"""Please generate a Material UI component based on the following prompt: {user_prompt}""",
                )
                print(f"Created message, ID: {message.id}") 
                
                run = project_client.agents.create_run(thread_id=thread_id, agent_id=UI_AGENT_ID)
                print(f"Created run, ID: {run.id}")
                tool_outputs_results = []  # Store all tool outputs
                
                while run.status in ["queued", "in_progress", "requires_action"]:
                    time.sleep(1)
                    run = project_client.agents.get_run(thread_id=thread_id, run_id=run.id)

                    if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                        tool_calls = run.required_action.submit_tool_outputs.tool_calls
                        if not tool_calls:
                            print("No tool calls provided - cancelling run")
                            project_client.agents.cancel_run(thread_id=thread_id, run_id=run.id)
                            break

                        for tool_call in tool_calls:
                            if isinstance(tool_call, RequiredFunctionToolCall):
                                try:
                                    print(f"Executing tool call: {tool_call}")
                                    output = function_tool.execute(tool_call)
                                    
                                    # Store the output directly
                                    tool_outputs_results.append({
                                        "tool_call_id": tool_call.id,
                                        "function_name": tool_call.function.name,
                                        "output": output
                                    })
                                except Exception as e:
                                    print(f"Error executing tool_call {tool_call.id}: {e}")
                        
                        # If we collected outputs, cancel the run instead of submitting
                        if tool_outputs_results:
                            print("Tool outputs collected, cancelling run")
                            project_client.agents.cancel_run(thread_id=thread_id, run_id=run.id)
                            break
                    
                    print(f"Current run status: {run.status}")

                if run.status == "failed":
                    logger.error(f"Extraction failed: {run.last_error}")
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        logger.info(f"Retrying in {wait_time} seconds... ({attempt+1}/{max_retries})")
                        time.sleep(wait_time)
                        continue  # Retry
                    else:
                        return {
                            "success": False,
                            "error": run.last_error,
                            "structured_data": None
                        }
                print(f"Run completed with status: {run.status}")
                if tool_outputs_results:
                    return {
                        "success": True,
                        "structured_data": tool_outputs_results[0]["output"]
                    }  # Return first tool output
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    wait_time = retry_delay * (attempt + 1)
                    logger.info(f"Rate limit hit. Waiting {wait_time}s before retry {attempt+1}/{max_retries}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Unexpected error in extraction: {e}")
                    if attempt == max_retries - 1:
                        return {
                            "success": False,
                            "error": str(e),
                            "structured_data": None
                        }

        return {
            "success": False,
            "error": "Max retries exceeded",
            "structured_data": None
        }

component_request="A card component with a heading New Note and a text area. The card should have a button to save the note. The card should be responsive and look good on mobile devices. The card should have a light pink color and a shadow effect. The text area should have a placeholder text 'Enter your note here...'. The button should have a primary color and a hover effect."

res=run_agent(component_request)
print(res)
if res["success"]:
    print("Generated component:")
    print(res["structured_data"]["description"])
    print(res["structured_data"]["imports"])
    print(res["structured_data"]["code"])

