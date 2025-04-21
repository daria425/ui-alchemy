from app.db.database_service_provider import DatabaseServiceProvider
from app.db.database_services import UserDatabaseService
def get_user_collection()->UserDatabaseService:
    return DatabaseServiceProvider.get_user_db_service()