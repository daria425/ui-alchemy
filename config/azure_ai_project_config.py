from dotenv import load_dotenv
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv()

def get_project_client():
    ai_foundry_connection_string=os.getenv("AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING")
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(), conn_str=ai_foundry_connection_string
    )
    return project_client

def close_project_client(project_client):
    project_client.close()



project_client=get_project_client()