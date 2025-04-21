from pymongo import MongoClient
from dotenv import load_dotenv
from app.utils.logger import logger
load_dotenv()
import os
MONGO_URI = os.getenv("MONGO_URI")

class DatabaseClient:
    _instance=None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseClient()
        return cls._instance
    
    def __init__(self):
        if DatabaseClient._instance is not None:
            raise Exception(" 🙅‍♀️ This class is a singleton 🙅‍♀️ Use get_instance() instead ✅")
        self.client=None
        self.db=None
        self.connect()
    def connect(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client["ui_alchemy"]
            logger.info("✅ Connected to MongoDB ✅")
        except Exception as e:
            logger.error(f"😵 Error connecting to MongoDB: {e} 😵")
            raise

    def close(self):
        if self.client:
            self.client.close()
            logger.info("🚪 MongoDB connection closed 🚪")
        else:
            logger.warning("⚠️ No MongoDB connection to close ⚠️")