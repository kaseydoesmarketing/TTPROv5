#!/usr/bin/env python3
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def test_private_key(key_string):
    """Test if a private key string can be loaded"""
    try:
        # Try to load the key
        private_key = serialization.load_pem_private_key(
            key_string.encode(),
            password=None,
            backend=default_backend()
        )
        print("✅ Private key format is VALID")
        return True
    except Exception as e:
        print(f"❌ Private key format is INVALID: {e}")
        return False

# Test with escaped newlines (WRONG format)
wrong_format = "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDVABbV93i24ViG\\nEccVLrYtkWA...\\n-----END PRIVATE KEY-----\\n"

# Test with real newlines (CORRECT format)
correct_format = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDVABbV93i24ViG
EccVLrYtkWA...
-----END PRIVATE KEY-----"""

print("Testing WRONG format (with \\n):")
test_private_key(wrong_format)

print("\nTesting CORRECT format (with real newlines):")
test_private_key(correct_format)