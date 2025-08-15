from fastapi import FastAPI, Depends, HTTPException, status, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
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
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .auth.auth0_verify import verify_auth0_id_token

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
	# Be permissive for previews and to rule out CORS misconfig
	allow_origin_regex=r"^https://.*$",
	allow_credentials=True,
	allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
	allow_headers=["Authorization","Content-Type","X-Requested-With"],
	expose_headers=["Content-Type","Content-Length"]
)

# ---- Auth router (Auth0 -> session cookie) ----
auth_router = APIRouter(prefix="/api/auth", tags=["auth"]) 
SESSION_COOKIE_NAME = "session_token"

def _cookie_domain_for_request(req: Request) -> Optional[str]:
	host = (req.headers.get("host") or "").lower()
	if host.endswith("titletesterpro.com"):
		return ".titletesterpro.com"
	return None

def _set_session_cookie(resp: JSONResponse, req: Request, raw: str, days: int = 7):
	domain = _cookie_domain_for_request(req)
	secure = True
	same_site = "none"
	expires = datetime.now(timezone.utc) + timedelta(days=days)
	resp.set_cookie(
		key=SESSION_COOKIE_NAME,
		value=raw,
		httponly=True,
		secure=secure,
		samesite=same_site,
		domain=domain,
		expires=expires
	)

def _clear_session_cookie(resp: JSONResponse, req: Request):
	domain = _cookie_domain_for_request(req)
	resp.delete_cookie(key=SESSION_COOKIE_NAME, domain=domain)

@auth_router.post("/login")
def auth_login(request: Request, db: Session = Depends(get_db)):
	auth = request.headers.get("authorization") or request.headers.get("Authorization")
	if not auth or not auth.lower().startswith("bearer "):
		raise HTTPException(status_code=401, detail="Missing bearer token")
	token = auth.split(" ", 1)[1].strip()
	try:
		claims = verify_auth0_id_token(token)
	except Exception as e:
		raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
	sub = claims.get("sub")
	if not sub:
		raise HTTPException(status_code=401, detail="Token missing subject")
	email = claims.get("email")
	name = claims.get("name") or email or "User"
	user = db.query(User).filter((User.firebase_uid == sub) | (User.email == email)).first()
	if not user:
		user = User(firebase_uid=sub, email=email, display_name=name)
		db.add(user)
	else:
		user.firebase_uid = user.firebase_uid or sub
		if email and not user.email:
			user.email = email
		if name and (not user.display_name or user.display_name == user.email):
			user.display_name = name
	import secrets, hashlib
	raw = secrets.token_urlsafe(48)
	user.session_token = hashlib.sha256(raw.encode()).hexdigest()
	user.session_expires = datetime.utcnow() + timedelta(days=7)
	db.commit()
	resp = JSONResponse({"ok": True, "user": {"id": user.id, "email": user.email, "display_name": user.display_name}})
	_set_session_cookie(resp, request, raw)
	return resp

@auth_router.post("/logout")
def auth_logout(request: Request, current: User = Depends(get_current_user_session), db: Session = Depends(get_db)):
	current.session_token = None
	current.session_expires = None
	db.commit()
	resp = JSONResponse({"ok": True})
	_clear_session_cookie(resp, request)
	return resp

@auth_router.get("/session")
def auth_session(current: User = Depends(get_current_user_session)):
	return {"ok": True, "user": {"id": current.id, "email": current.email, "display_name": current.display_name}}

app.include_router(auth_router)

app.include_router(ab_test_router)
app.include_router(channel_router)
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router)

# OAuth routes
from .oauth_routes import router as oauth_router
app.include_router(oauth_router)

# Explicit google oauth alias route wiring (compat)
from .google_oauth_routes import router as google_oauth_router
app.include_router(google_oauth_router)

# Debug and inspection utilities
import base64
import json

@app.get("/api/meta/cors")
async def meta_cors(request: Request):
	return {
		"ok": True,
		"origin_header": request.headers.get("origin"),
		"allowed_list": ALLOWED_ORIGINS,
	}
