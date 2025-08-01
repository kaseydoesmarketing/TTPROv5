#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from datetime import datetime

def create_test_user():
    """Create a test user for Celery task testing"""
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.id == "dev-user-123").first()
        if existing_user:
            print("Test user already exists")
            return existing_user
        
        test_user = User(
            id="dev-user-123",
            firebase_uid="dev-firebase-uid-123",
            email="dev-test@example.com",
            display_name="Dev Test User",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        
        print(f"Created test user: {test_user.id}")
        return test_user
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
