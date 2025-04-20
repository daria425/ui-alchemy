import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = "2025-01-01-preview"

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "ui_alchemy"
CHECKPOINT_COLLECTION = "sessions"

# Base directory for relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This is /home/vboxuser/repos/ui-alchemy/app/agent/

# File paths - corrected to point directly to agent_instructions.txt in the same directory
UI_GEN_AGENT_INSTRUCTIONS_PATH = os.path.join(BASE_DIR, "ui_gen_agent_instructions.txt")
VALIDATION_AGENT_INSTRUCTIONS_PATH = os.path.join(BASE_DIR, "validation_agent_instructions.txt")
UNDERSTAND_REQUIREMENTS_INSTRUCTIONS_PATH = os.path.join(BASE_DIR, "understand_requirements_instructions.txt")
SELECT_LIBRARIES_INSTRUCTIONS_PATH = os.path.join(BASE_DIR, "select_libraries_instructions.txt")