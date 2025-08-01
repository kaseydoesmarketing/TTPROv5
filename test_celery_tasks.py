#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.celery_app import celery_app
from app.tasks import update_quota_usage, rotate_titles

def test_quota_usage_task():
    """Test the update_quota_usage task"""
    print("Testing update_quota_usage task...")
    
    result = update_quota_usage.delay("dev-user-123", "videos_list", 1)
    print(f"Task ID: {result.id}")
    print(f"Task state: {result.state}")
    
    try:
        task_result = result.get(timeout=10)
        print(f"Task completed successfully: {task_result}")
        return True
    except Exception as e:
        print(f"Task failed: {e}")
        return False

def test_rotate_titles_task():
    """Test the rotate_titles task"""
    print("\nTesting rotate_titles task...")
    
    result = rotate_titles.delay()
    print(f"Task ID: {result.id}")
    print(f"Task state: {result.state}")
    
    try:
        task_result = result.get(timeout=10)
        print(f"Task completed successfully: {task_result}")
        return True
    except Exception as e:
        print(f"Task failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Celery background tasks...")
    
    quota_success = test_quota_usage_task()
    
    rotate_success = test_rotate_titles_task()
    
    print(f"\nResults:")
    print(f"Quota usage task: {'PASS' if quota_success else 'FAIL'}")
    print(f"Rotate titles task: {'PASS' if rotate_success else 'FAIL'}")
    
    if quota_success and rotate_success:
        print("\nAll Celery tasks are working correctly!")
        sys.exit(0)
    else:
        print("\nSome Celery tasks failed!")
        sys.exit(1)
