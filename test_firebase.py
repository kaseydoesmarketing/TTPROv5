#!/usr/bin/env python3
"""Test Firebase Admin SDK configuration and custom token creation"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.firebase_auth import initialize_firebase, create_custom_token
from app.config import settings
import firebase_admin
from firebase_admin import auth
import json

def test_firebase_config():
    print("Testing Firebase Admin SDK Configuration...")
    print(f"Project ID: {settings.firebase_project_id}")
    print(f"Client Email: {settings.firebase_client_email}")
    print(f"Client ID: {settings.firebase_client_id}")
    print()

def test_custom_token_creation():
    print("Testing Custom Token Creation...")
    
    # Initialize Firebase
    initialize_firebase()
    
    # Test different UID formats
    test_uids = [
        "100702787282198055542",
        "google_100702787282198055542",
        "google:100702787282198055542"
    ]
    
    additional_claims = {
        "email": "liftedkulture-6202@pages.plusgoogle.com",
        "name": "Maschine Kulture TV",
        "email_verified": True
    }
    
    for uid in test_uids:
        try:
            print(f"\nTesting UID: {uid}")
            token = create_custom_token(uid, additional_claims)
            print(f"✓ Token created successfully")
            print(f"  Token length: {len(token)}")
            print(f"  Token preview: {token[:50]}...")
            
            # Decode token to check structure
            import jwt
            decoded = jwt.decode(token, options={"verify_signature": False})
            print(f"  Token claims: {json.dumps(decoded, indent=2)}")
            
        except Exception as e:
            print(f"✗ Failed to create token: {e}")

def test_existing_user():
    print("\nTesting existing Firebase user...")
    try:
        # Try to get user with different UIDs
        test_uids = [
            "google:100702787282198055542",
            "google_100702787282198055542",
            "100702787282198055542"
        ]
        
        for uid in test_uids:
            try:
                user = auth.get_user(uid)
                print(f"✓ Found user with UID: {uid}")
                print(f"  Email: {user.email}")
                print(f"  Display Name: {user.display_name}")
                print(f"  Provider Data: {user.provider_data}")
                break
            except auth.UserNotFoundError:
                print(f"✗ No user found with UID: {uid}")
            except Exception as e:
                print(f"✗ Error getting user {uid}: {e}")
    except Exception as e:
        print(f"Error in user lookup: {e}")

if __name__ == "__main__":
    test_firebase_config()
    print("\n" + "="*50 + "\n")
    test_custom_token_creation()
    print("\n" + "="*50 + "\n")
    test_existing_user()