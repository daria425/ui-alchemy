from langchain_core.tools import tool

@tool
def ui_gen_function(install_script: str, imports: str, code: str, description: str):
    """
    Function to generate a UI component
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