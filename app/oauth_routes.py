from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict
import hmac, hashlib, json
from datetime import datetime, timedelta

from .config import settings
from .database import get_db
from .models import User
from .auth_dependencies import get_current_user_session

router = APIRouter(prefix="/api/oauth/google", tags=["oauth-google"])


def verify_hmac(request_body: bytes, header_value: str) -> bool:
	secret = (settings.auth0_action_hmac_secret or "").encode()
	if not secret:
		return False
	computed_hex = hmac.new(secret, request_body, hashlib.sha256).hexdigest()
	if not header_value:
		return False
	val = header_value.strip().lower()
	if val.startswith("sha256="):
		val = val.split("=", 1)[1]
	return hmac.compare_digest(computed_hex, val)


@router.post("/store")
async def store_tokens(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
	"""
	Auth0 Action posts Google tokens here after a successful Google login/link.
	Headers: X-Auth0-Actions-Signature: sha256=<hex(hmac_sha256(body, secret))>
	Body JSON: { sub, email?, access_token, refresh_token?, scope?, expires_in?, issued_at? }
	"""
	body = await request.body()
	sig = (
		request.headers.get("x-auth0-actions-signature")
		or request.headers.get("X-Auth0-Actions-Signature")
		or request.headers.get("x-signature")
	)
	if not verify_hmac(body, sig):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
	data = json.loads(body.decode())
	sub = data.get("sub")
	email = data.get("email")
	access_token = data.get("access_token")
	refresh_token = data.get("refresh_token")
	scope = data.get("scope")
	expires_in = int(data.get("expires_in") or 3600)
	if not sub or not access_token:
		raise HTTPException(status_code=400, detail="Missing required fields")
	user = db.query(User).filter((User.firebase_uid == sub) | (User.email == email)).first()
	if not user:
		# minimal create if needed (email may be absent)
		user = User(firebase_uid=sub, email=email or f"user-{sub}@example.com", display_name=email or "User")
		db.add(user)
	user.set_google_tokens(access_token, refresh_token, expires_in, scope)
	user.updated_at = datetime.utcnow()
	db.commit()
	return {"ok": True, "scope": scope, "expires_at": user.token_expires_at.isoformat() if user.token_expires_at else None}


@router.get("/status")
async def google_status(current: User = Depends(get_current_user_session)):
	connected = bool(current.google_refresh_token)
	return {
		"connected": connected,
		"scope": current.google_scope if connected else None,
		"expiresAt": current.token_expires_at.isoformat() if current.token_expires_at else None,
	}


@router.post("/revoke")
async def revoke_stub():
	return {"ok": False, "detail": "Revoke not implemented yet"} 