import firebase_admin
from firebase_admin import credentials
import os
from app.utils.logger import logger
class FirebaseConfig:
    _instance=None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance=FirebaseConfig()
        return cls._instance
    
    def __init__(self):
        if FirebaseConfig._instance is not None:
            raise Exception(" 🙅‍♀️ The FirebaseConfig class is a singleton 🙅‍♀️ Use get_instance() instead ✅")
        self.app=None
    
    def initialize_firebase_app(self):
        """Initialize Firebase Admin SDK"""
        if not self.app:
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                firebase_keyfile_path = os.path.join(current_dir, "firebase_key.json")
                
                # Check if file exists
                if not os.path.exists(firebase_keyfile_path):
                    logger.error(f"Firebase key file not found at {firebase_keyfile_path}")
                
                cred = credentials.Certificate(firebase_keyfile_path)
                self.app = firebase_admin.initialize_app(cred)
                logger.info("🔥 Firebase Admin SDK initialized 🔥")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Firebase: {e} ❌")




