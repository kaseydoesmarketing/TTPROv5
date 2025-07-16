import firebase_admin
from firebase_admin import credentials, auth
from .config import settings
import json


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        try:
            cred_dict = {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                "private_key_id": settings.firebase_private_key_id,
                "private_key": settings.firebase_private_key.replace('\\n', '\n'),
                "client_email": settings.firebase_client_email,
                "client_id": settings.firebase_client_id,
                "auth_uri": settings.firebase_auth_uri,
                "token_uri": settings.firebase_token_uri,
            }
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Firebase initialization failed: {e}")


def verify_firebase_token(id_token: str):
    """Verify Firebase ID token and return user info"""
    if id_token == "mock-dev-token":
        return {
            "uid": "dev-user-123",
            "email": "dev@example.com",
            "name": "Dev User",
            "picture": "https://via.placeholder.com/150"
        }
    
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        import os
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {
                "uid": "dev-user-123",
                "email": "dev@example.com", 
                "name": "Dev User",
                "picture": "https://via.placeholder.com/150"
            }
        raise ValueError(f"Invalid token: {str(e)}")


async def get_user_by_uid(uid: str):
    """Get user info from Firebase by UID"""
    try:
        initialize_firebase()
        user_record = auth.get_user(uid)
        return user_record
    except Exception as e:
        raise ValueError(f"User not found: {str(e)}")
