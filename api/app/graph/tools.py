from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class UIGenSchema(BaseModel):
    """
    Schema for UI generation
    """
    code: str = Field(..., description="The code for the component")

def ui_gen_function(code: str):
    """
    Function to generate a UI component

    :param code: The code for the component
    :return: A dictionary containing the code
    """
    return {

        "code": code,
    }

structured_ui_gen_tool=StructuredTool.from_function(ui_gen_function, args_schema=UIGenSchema, name="UiGenTool", description="A tool to generate a UI component")