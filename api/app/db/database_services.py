from app.db.database_client import DatabaseClient
from app.utils.logger import logger
from pymongo.collection import Collection
from datetime import datetime, timezone
class BaseDatabaseService:
    """
    Base class for db collections
    """
    def __init__(self, collection_name: str):
        self.db_client = DatabaseClient.get_instance()
        self._collection_name = collection_name
        self._collection=None

    @property
    def collection(self)->Collection:
        """
        Get the collection object
        """
        if self._collection is None:
            if self.db_client.db is None:
                self.db_client.connect()
            self._collection = self.db_client.db[self._collection_name]
        return self._collection
    
    def insert_one(self, data: dict):
        """
        Insert a single document into the collection
        """
        try:
            result=self.collection.insert_one(data)
            return result
        except Exception as e:
            logger.error(f"❌ Error inserting document: {e} ❌")
            raise

    def find_one(self, query: dict, projection: dict = {"_id":0}):
        """
        Find a single document in the collection
        """
        try:
            result=self.collection.find_one(query, projection )
            return result
        except Exception as e:
            logger.error(f"❌ Error finding document: {e} ❌")
            raise

    def update_one(self, query: dict, update: dict):
        """
        Update a single document in the collection
        """
        try:
            result=self.collection.update_one(query, update)
            return result
        except Exception as e:
            logger.error(f"❌ Error updating document: {e} ❌")
            raise

    def find_many(self, query: dict, projection: dict = {"_id":0}):
        """
        Find many documents in the collection
        """
        try:
            cursor=self.collection.find(query, projection)
            results = list(cursor)
            return results
        except Exception as e:
            logger.error(f"❌ Error finding documents: {e} ❌")
            raise

class UserDatabaseService(BaseDatabaseService):
    """
    User database service
    """
    def __init__(self):
        super().__init__("users")
    
    def find_user_by_uid(self, uid: str):
        """
        Find user by uid
        """
        try:
            result=self.collection.find_one({"uid": uid})
            return result
        except Exception as e:
            logger.error(f"❌ Error finding user by uid: {e} ❌")
            raise

    def login_user(self, user_data:dict):
        uid=user_data["uid"]
        existing_user=self.find_user_by_uid(uid)
        if existing_user:
                logger.info(f"Found existing user, returning data for {existing_user['uid']}")
                if "_id" in existing_user:
                    existing_user["_id"]=str(existing_user["_id"])
                return existing_user
        inserted_doc=self.insert_one(user_data)
        logger.info(f"Successfully inserted user {inserted_doc.inserted_id}")
        print(f"Inserted user data: {user_data}")
        if "_id" in user_data:
            user_data["_id"]=str(user_data["_id"])
        return user_data
    
class SessionDatabaseService(BaseDatabaseService):
    def __init__(self):
        super().__init__("sessions")
    
    def update_session_metadata(self, session_id: str):
        """
        Update a session
        """
        update={"configurable.metadata.updated_at": datetime.now(timezone.utc)}
        try:
            result=self.update_one({"session_id": session_id}, {"$set": update})
            return result
        except Exception as e:
            logger.error(f"❌ Error updating session: {e} ❌")
            raise