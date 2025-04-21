
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routes import sessions
from contextlib import asynccontextmanager
from app.db.database_client import DatabaseClient




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    """
    db_client_instance = DatabaseClient.get_instance()
    db_client_instance.connect()
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