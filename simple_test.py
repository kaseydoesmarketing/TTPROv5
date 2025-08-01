#!/usr/bin/env python3
"""Simple test to check if the app can start without Firebase"""

import os
import sys

# Set development mode to bypass Firebase
os.environ['VITE_FIREBASE_API_KEY'] = 'dev_mode_testing'
os.environ['ENVIRONMENT'] = 'development'

# Add current directory to path
sys.path.insert(0, '.')

try:
    from app.main import app
    print("✅ App imported successfully!")
    
    # Test a simple endpoint
    import uvicorn
    print("🚀 Starting server on http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Installing missing dependencies...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()