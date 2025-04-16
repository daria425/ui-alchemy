import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.azure_ai_project_config import project_client
import time
from azure.ai.projects.models import (
    FunctionTool,
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
)
from utils.file_utils import load_file
from utils.logger import logger, shut_up_azure_logging
from dotenv import load_dotenv

load_dotenv()
shut_up_azure_logging()
UI_AGENT_ID = os.getenv("UI_AGENT_ID")
instruction_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "agent_instructions.txt"
)


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


class UIGenAgent:
    def __init__(self):
        self.project_client = project_client
        self.ui_agent_id = UI_AGENT_ID
        self.functions = FunctionTool(functions=[ui_gen_function])

    def setup_agent(self):
        """
        Setup the agent with the provided instructions and tools
        """
        try:
            ui_gen_instructions = load_file(instruction_file_path)
            self.project_client.agents.update_agent(
                agent_id=self.ui_agent_id,
                instructions=ui_gen_instructions,
                tools=self.functions.definitions,
            )
        except Exception as e:
            logger.error(f"Error setting up agent: {e}")

    def start_conversation(self, user_prompt: str):
        """
        Start a conversation with the agent
        :param user_prompt: The prompt to start the conversation
        """
        try:
            thread = self.project_client.agents.create_thread()
            thread_id = thread.id
            message = self.project_client.agents.create_message(
                thread_id=thread_id,
                role="user",
                content=f"""Act as a requirements analyst. 
                Given the following user request: "{user_prompt}"
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
                """,
            )
            print(f"Created initial message, ID: {message.id}")
            run = self.project_client.agents.create_run(
                thread_id=thread_id, agent_id=self.ui_agent_id
            )
            run_id = run.id
            print(f"Created initial run, ID: {run_id}")

            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                time.sleep(1)
                run = self.project_client.agents.get_run(
                    thread_id=thread_id, run_id=run_id
                )
                print(f"Initial run status: {run.status}")

            # Get the agent's response
            messages = self.project_client.agents.list_messages(
                thread_id=thread_id, run_id=run_id
            )
            last_msg = messages.get_last_text_message_by_role("assistant")
            print(last_msg)
            if last_msg:
                if "yes" in last_msg.text["value"].lower():
                    return {
                        "status": "success",
                        "message": "Agent indicated enough information.",
                        "thread_id": thread_id,
                        "user_prompt": user_prompt,
                    }

                else:
                    print("Agent indicated not enough information.")
                    return {
                        "status": "needs_more_info",
                        "message": "Agent indicated not enough information.",
                        "prompt": user_prompt,
                        "thread_id": thread_id,
                        "user_prompt": user_prompt,
                    }
            else:
                print("No response from agent.")
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")

    def continue_conversation(self, thread_id: str, user_prompt: str):
        """
        Continue the conversation with the agent
        :param thread_id: The ID of the thread to continue the conversation
        :param user_prompt: The prompt to continue the conversation
        """
        try:
            message = self.project_client.agents.create_message(
                thread_id=thread_id,
                role="user",
                content=f"""Act as a requirements analyst. 
                Given the following user request: "{user_prompt}"
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
                """,
            )
            print(f"Created follow-up message, ID: {message.id}")
            run = self.project_client.agents.create_run(
                thread_id=thread_id, agent_id=self.ui_agent_id
            )
            run_id = run.id
            print(f"Created follow-up run, ID: {run_id}")
            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                time.sleep(1)
                run = self.project_client.agents.get_run(
                    thread_id=thread_id, run_id=run_id
                )
                print(f"Follow-up run status: {run.status}")
            messages = self.project_client.agents.list_messages(
                thread_id=thread_id, run_id=run_id
            )
            last_msg = messages.get_last_text_message_by_role("assistant")
            if last_msg:
                if "yes" in last_msg.text["value"].lower():
                    return {
                        "status": "success",
                        "message": "Agent indicated enough information.",
                        "thread_id": thread_id,
                        "user_prompt": user_prompt,
                    }

                else:
                    print("Agent indicated not enough information.")
                    return {
                        "status": "needs_more_info",
                        "message": "Agent indicated not enough information.",
                        "prompt": user_prompt,
                        "thread_id": thread_id,
                        "user_prompt": user_prompt,
                    }
            else:
                print("No response from agent.")
                return {
                    "status": "error",
                    "message": "No response from agent.",
                    "thread_id": thread_id,
                    "user_prompt": user_prompt,
                }
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return {
                "status": "error",
                "message": f"Error continuing conversation: {e}",
                "thread_id": thread_id,
                "user_prompt": user_prompt,
            }

    def provide_additional_info(self, thread_id, user_prompt):
        """
        Provide additional information to the agent
        """
        try:
            message = self.project_client.agents.create_message(
                thread_id=thread_id,
                role="user",
                content=f"""
Act as a UI designer. Ask a series of follow up questions to gather more information about the request to generate the following component: "{user_prompt}"
1. Ask about the specific design elements needed (e.g., colors, styles, layout).
2. Inquire about the functionality and behavior of the component (e.g., click handlers, data binding).
3. Clarify the context in which the component will be used (e.g., part of a larger application, standalone).
4. Be conscise. No yapping.
""",
            )
            print(f"Created follow-up message, ID: {message.id}")
            run = self.project_client.agents.create_run(
                thread_id=thread_id, agent_id=self.ui_agent_id
            )
            run_id = run.id
            print(f"Created follow-up run, ID: {run_id}")
            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                time.sleep(1)
                run = self.project_client.agents.get_run(
                    thread_id=thread_id, run_id=run_id
                )
                print(f"Follow-up run status: {run.status}")
            agent_response = self.project_client.agents.list_messages(
                thread_id=thread_id, run_id=run_id
            )
            last_msg = agent_response.get_last_text_message_by_role("assistant")
            return {
                    "message": last_msg.text["value"],
                    "thread_id": thread_id,
                }
        except Exception as e:
            logger.error(f"Error providing additional information: {e}")

    def generate_component(self, thread_id: str, user_prompt: str):
        max_retries = 3
        retry_delay = 30  # seconds

        for attempt in range(max_retries):
            try:
                message = self.project_client.agents.create_message(
                    thread_id=thread_id,
                    role="user",
                    content=f"""Please generate a Material UI component based on the following prompt: {user_prompt}""",
                )
                print(f"Created message, ID: {message.id}")

                run = self.project_client.agents.create_run(
                    thread_id=thread_id, agent_id=self.ui_agent_id
                )
                print(f"Created run, ID: {run.id}")
                tool_outputs_results = []  # Store all tool outputs

                while run.status in ["queued", "in_progress", "requires_action"]:
                    time.sleep(1)
                    run = self.project_client.agents.get_run(
                        thread_id=thread_id, run_id=run.id
                    )

                    if run.status == "requires_action" and isinstance(
                        run.required_action, SubmitToolOutputsAction
                    ):
                        tool_calls = run.required_action.submit_tool_outputs.tool_calls
                        if not tool_calls:
                            print("No tool calls provided - cancelling run")
                            self.project_client.agents.cancel_run(
                                thread_id=thread_id, run_id=run.id
                            )
                            break
                        for tool_call in tool_calls:
                            if isinstance(tool_call, RequiredFunctionToolCall):
                                try:
                                    print(f"Executing tool call: {tool_call}")
                                    output = self.functions.execute(tool_call)

                                    tool_outputs_results.append(
                                        {
                                            "tool_call_id": tool_call.id,
                                            "function_name": tool_call.function.name,
                                            "output": output,
                                        }
                                    )
                                except Exception as e:
                                    print(
                                        f"Error executing tool_call {tool_call.id}: {e}"
                                    )

                        # If we collected outputs, cancel the run instead of submitting
                        if tool_outputs_results:
                            print("Tool outputs collected, cancelling run")
                            self.project_client.agents.cancel_run(
                                thread_id=thread_id, run_id=run.id
                            )
                            break

                    print(f"Current run status: {run.status}")

                if run.status == "failed":
                    logger.error(f"Run failed: {run.last_error}")
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        logger.info(
                            f"Retrying in {wait_time} seconds... ({attempt+1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        continue  # Retry
                    else:
                        return {
                            "success": False,
                            "error": run.last_error,
                            "structured_data": None,
                        }
                print(f"Run completed with status: {run.status}")
                if tool_outputs_results:
                    return {
                        "success": True,
                        "structured_data": tool_outputs_results[0]["output"],
                    }  # Return first tool output
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    wait_time = retry_delay * (attempt + 1)
                    logger.info(
                        f"Rate limit hit. Waiting {wait_time}s before retry {attempt+1}/{max_retries}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Unexpected error in extraction: {e}")
                    if attempt == max_retries - 1:
                        return {
                            "success": False,
                            "error": str(e),
                            "structured_data": None,
                        }
        return {
            "success": False,
            "error": "Max retries exceeded",
            "structured_data": None,
        }
    
    def edit_component(self, thread_id: str, user_prompt: str, component:str):
        """
        Edit the component based on user feedback
        :param thread_id: The ID of the thread to edit the component
        :param user_prompt: The feedback from the user
        """
        max_retries = 3
        retry_delay = 30  # seconds

        for attempt in range(max_retries):
            try:
                message = self.project_client.agents.create_message(
                    thread_id=thread_id,
                    role="user",
                    content=f"""Please edit the following component:
                    {component}
                    Based on the following feedback: {user_prompt}""",
                )
                print(f"Created message, ID: {message.id}", f"Message content:{message.content}")

                run = self.project_client.agents.create_run(
                    thread_id=thread_id, agent_id=self.ui_agent_id
                )
                print(f"Created run, ID: {run.id}")
                tool_outputs_results = []  # Store all tool outputs

                while run.status in ["queued", "in_progress", "requires_action"]:
                    time.sleep(1)
                    run = self.project_client.agents.get_run(
                        thread_id=thread_id, run_id=run.id
                    )

                    if run.status == "requires_action" and isinstance(
                        run.required_action, SubmitToolOutputsAction
                    ):
                        tool_calls = run.required_action.submit_tool_outputs.tool_calls
                        if not tool_calls:
                            print("No tool calls provided - cancelling run")
                            self.project_client.agents.cancel_run(
                                thread_id=thread_id, run_id=run.id
                            )
                            break
                        for tool_call in tool_calls:
                            if isinstance(tool_call, RequiredFunctionToolCall):
                                try:
                                    print(f"Executing tool call: {tool_call}")
                                    output = self.functions.execute(tool_call)

                                    tool_outputs_results.append(
                                        {
                                            "tool_call_id": tool_call.id,
                                            "function_name": tool_call.function.name,
                                            "output": output,
                                        }
                                    )
                                except Exception as e:
                                    print(
                                        f"Error executing tool_call {tool_call.id}: {e}"
                                    )

                        # If we collected outputs, cancel the run instead of submitting
                        if tool_outputs_results:
                            print("Tool outputs collected, cancelling run")
                            self.project_client.agents.cancel_run(
                                thread_id=thread_id, run_id=run.id
                            )
                            break

                    print(f"Current run status: {run.status}")

                if run.status == "failed":
                    logger.error(f"Run failed: {run.last_error}")
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        logger.info(
                            f"Retrying in {wait_time} seconds... ({attempt+1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        continue  # Retry
                    else:
                        return {
                            "success": False,
                            "error": run.last_error,
                            "structured_data": None,
                            "thread_id": thread_id,
                        }
                print(f"Run completed with status: {run.status}")
                if tool_outputs_results:
                    return {
                        "success": True,
                        "structured_data": tool_outputs_results[0]["output"],
                        "thread_id": thread_id,
                    }  # Return first tool output
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    wait_time = retry_delay * (attempt + 1)
                    logger.info(
                        f"Rate limit hit. Waiting {wait_time}s before retry {attempt+1}/{max_retries}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Unexpected error in extraction: {e}")
                    if attempt == max_retries - 1:
                        return {
                            "success": False,
                            "error": str(e),
                            "structured_data": None,
                            "thread_id": thread_id,
                        }
        return {
            "success": False,
            "error": "Max retries exceeded",
            "structured_data": None,
            "thread_id":thread_id
        }

    def run_agent(self, user_prompt: str):
        """
        Run the agent with the provided user prompt
        :param user_prompt: The prompt to run the agent with
        """
        # Start conversation
        response = self.start_conversation(user_prompt)
        if response["status"] == "needs_more_info":
            # Provide additional information
            additional_info = self.provide_additional_info(
                response["thread_id"], user_prompt
            )
            print("\n" + additional_info["message"])
            conversation_history = user_prompt
            while True:
                user_input = input(
                    "Your response (type 'generate' to generate the component) >"
                )
                if user_input.lower() == "generate":
                    break
                conversation_history += " " + user_input
                response = self.continue_conversation(
                    response["thread_id"], conversation_history
                )
                if response["status"] == "needs_more_info":
                    additional_info = self.provide_additional_info(
                        response["thread_id"], conversation_history
                    )
                    print("\n" + additional_info["message"])
                elif response["status"] == "success":
                    print("Agent indicated enough information.")
                    break
            component_response = self.generate_component(
                response["thread_id"], conversation_history
            )
            print(component_response)
            return {
                **component_response, "thread_id": response["thread_id"]
            }
        elif response["status"] == "success":
            component_response = self.generate_component(
                response["thread_id"], user_prompt
            )
            print(component_response)
            return {
                **component_response, "thread_id": response["thread_id"]
            }
        else:
            print("Error in conversation setup.")


if __name__ == "__main__":
    print("Starting UI Generation Agent...")
    agent = UIGenAgent()
    agent.setup_agent()
    last_component_str=None
    last_thread_id=None

    while True:
        if last_component_str:
            action=input("\nWhat would you like to do?\n1. Generate new component\n2. Edit current component\n3. Exit\nChoice (1/2/3): ")
            if action == "1":
                last_component_str=None
                last_thread_id=None
            elif action == "2":
                user_feedback = input("Please provide your feedback on the current component: ")
                component_response = agent.edit_component(
                    last_thread_id, user_feedback, last_component_str
                )
                if component_response["success"]:
                    last_component_str="\n\n".join(component_response["structured_data"].values())
                    last_component=component_response["structured_data"]
                    last_thread_id = component_response["thread_id"]
                    print("Component edited successfully.")
                    if last_component:
                        print("Install Script:", last_component["install_script"])
                        print("Imports:", last_component["imports"])
                        print("Code:", last_component["code"])
                        print("Description:", last_component["description"])
                else:
                    print("Error editing component:", component_response["error"])
            elif action == "3":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
                continue
        user_prompt = input("Please enter the kind of component you would like: ")
        if user_prompt.lower() == "exit":
            print("Exiting...")
            break
        component_response = agent.run_agent(user_prompt)
        if component_response["success"]:
            last_component_str="\n\n".join(component_response["structured_data"].values())
            last_component=component_response["structured_data"]
            last_thread_id = component_response["thread_id"]
            print("Component generated successfully.")
            if last_component:
                print("Install Script:", last_component["install_script"])
                print("Imports:", last_component["imports"])
                print("Code:", last_component["code"])
                print("Description:", last_component["description"])
        else:
            print("Error generating component:", component_response["error"])
