from app.db.database_services import UserDatabaseService, SessionDatabaseService
class DatabaseServiceProvider:
    _user_db_service = None
    _session_db_service = None

    @classmethod
    def get_user_db_service(cls):
        if cls._user_db_service is None:
            cls._user_db_service = UserDatabaseService()
        return cls._user_db_service
    
    @classmethod
    def get_session_db_service(cls):
        if cls._session_db_service is None:
            cls._session_db_service = SessionDatabaseService()
        return cls._session_db_service
