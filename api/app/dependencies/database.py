from app.db.database_service_provider import DatabaseServiceProvider
from app.db.database_services import UserDatabaseService, SessionDatabaseService
def get_user_collection()->UserDatabaseService:
    return DatabaseServiceProvider.get_user_db_service()

def get_session_collection()->SessionDatabaseService:
    return DatabaseServiceProvider.get_session_db_service()