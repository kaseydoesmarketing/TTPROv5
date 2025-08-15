from fastapi import FastAPI, Depends, HTTPException, status, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .config import settings
from .database import get_db
from .database_manager import db_manager

from .models import User
from .ab_test_routes import router as ab_test_router
from .channel_routes import router as channel_router
from .billing_routes import router as billing_router
from .admin_routes import router as admin_router
from .auth_dependencies import get_current_user_session
import logging
import asyncio
import requests
import os
import jwt
from jwt import PyJWKClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

processed_auth_codes = set()

app = FastAPI(
    title="TitleTesterPro API",
    description="A SaaS platform for A/B testing YouTube titles - Render Deployment",
    version="1.0.7"
)

# CRITICAL: Health check endpoint MUST be defined before ANY middleware
# This ensures Render can always reach it during deployment
@app.get("/")
def root():
    """Root endpoint for Render health checks"""
    return {"status": "healthy", "service": "TitleTesterPro API", "platform": "render"}

@app.get("/debug/database")
def debug_database():
    """Debug database connection status"""
    import os
    from .database_manager import db_manager
    
    database_url = os.getenv("DATABASE_URL", "NOT SET")
    is_external = ".render.com" in database_url
    
    try:
        # Try to get a connection
        if db_manager.engine:
            with db_manager.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                db_status = "connected"
        else:
            db_status = "no engine"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "database_url_set": database_url != "NOT SET",
        "database_url_is_external": is_external,
        "database_url_preview": database_url[:50] + "..." if len(database_url) > 50 else database_url,
        "database_status": db_status,
        "db_manager_initialized": db_manager._initialized,
        "engine_exists": db_manager.engine is not None
    }

@app.get("/healthz")
def healthz():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/health")
async def health_check_simple():
    """Simple health check that responds immediately without database dependencies"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "titletesterpro-api"
    }

# Deterministic CORS configuration
ALLOWED_ORIGINS = [
    "https://www.titletesterpro.com",
    "https://titletesterpro.com",
    "https://app.titletesterpro.com",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https://.*ttpro(v5|[-]?ov5)?.*vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type","X-Requested-With"],
    expose_headers=["Content-Type","Content-Length"]
)

app.include_router(ab_test_router)
app.include_router(channel_router)
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router)

# OAuth routes
from .oauth_routes import router as oauth_router
app.include_router(oauth_router)

# Debug and inspection utilities
import base64
import json
