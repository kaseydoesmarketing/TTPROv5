#!/usr/bin/env python3
"""Verify Firebase private key can be used to sign JWTs"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def verify_private_key():
    """Verify the Firebase private key is valid"""
    try:
        print("Verifying Firebase private key...")
        
        # Get the private key
        private_key_str = settings.firebase_private_key.replace('\\n', '\n')
        
        # Try to load it
        private_key = serialization.load_pem_private_key(
            private_key_str.encode(),
            password=None,
            backend=default_backend()
        )
        
        print("✓ Private key loaded successfully")
        
        # Try to create a test JWT
        test_payload = {"test": "data", "uid": "test123"}
        test_token = jwt.encode(
            test_payload,
            private_key,
            algorithm="RS256",
            headers={"kid": settings.firebase_private_key_id}
        )
        
        print(f"✓ Test JWT created successfully")
        print(f"  Token length: {len(test_token)}")
        print(f"  Token preview: {test_token[:50]}...")
        
        # Verify we can decode it
        public_key = private_key.public_key()
        decoded = jwt.decode(test_token, public_key, algorithms=["RS256"])
        print(f"✓ Token decoded successfully: {decoded}")
        
    except Exception as e:
        print(f"✗ Error verifying private key: {e}")
        print(f"  Error type: {type(e).__name__}")
        
def check_firebase_project():
    """Check if the Firebase project ID matches what's expected"""
    print("\nChecking Firebase project configuration...")
    print(f"Project ID from .env: {settings.firebase_project_id}")
    print(f"Client email domain: {settings.firebase_client_email.split('@')[1] if '@' in settings.firebase_client_email else 'N/A'}")
    
    # Check if they match
    expected_domain = f"{settings.firebase_project_id}.iam.gserviceaccount.com"
    actual_domain = settings.firebase_client_email.split('@')[1] if '@' in settings.firebase_client_email else ''
    
    if actual_domain == expected_domain:
        print("✓ Project ID and client email domain match")
    else:
        print(f"✗ Mismatch: Expected domain {expected_domain}, got {actual_domain}")

if __name__ == "__main__":
    verify_private_key()
    check_firebase_project()