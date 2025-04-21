from app.db.database_services import UserDatabaseService
class DatabaseServiceProvider:
    _user_db_service = None

    @classmethod
    def get_user_db_service(cls):
        if cls._user_db_service is None:
            cls._user_db_service = UserDatabaseService()
        return cls._user_db_service
