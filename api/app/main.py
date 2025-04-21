
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routes import sessions
from contextlib import asynccontextmanager
from app.db.database_client import DatabaseClient
from app.config.firebase_config import FirebaseConfig




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    """
    # Initialize UI Alchemy

    db_client_instance = DatabaseClient.get_instance()
    firebase_app_instance = FirebaseConfig.get_instance()

    # Connections
    firebase_app_instance.initialize_firebase_app()
    db_client_instance.connect()
    from app.agent.ui_alchemy import initialize_ui_alchemy
    initialize_ui_alchemy()
    yield
    db_client_instance.close()

app = FastAPI(lifespan=lifespan)
# Enable CORS
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)