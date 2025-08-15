from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from .database import get_db
from .models import User
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

async def get_current_user_session(
	request: Request,
	db: Session = Depends(get_db)
) -> User:
	"""
	Get current user from session cookie.
	"""
	try:
		session_token = request.cookies.get("session_token")
		if not session_token:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No active session.")
		session_hash = hashlib.sha256(session_token.encode()).hexdigest()
		user = db.query(User).filter(
			User.session_token == session_hash,
			User.session_expires > datetime.utcnow(),
			User.is_active == True
		).first()
		if not user:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid.")
		return user
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Session authentication error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication system error")

async def get_current_paid_user(
	current_user: User = Depends(get_current_user_session)
) -> User:
	"""Require user to have active subscription (allowlisted emails bypass)."""
	authorized_emails = [
		"liftedkulture@gmail.com",
		"liftedkulture-6202@pages.plusgoogle.com",
		"Shemeka.womenofexcellence@gmail.com"
	]
	if current_user.email in authorized_emails:
		return current_user
	if current_user.subscription_status not in ["active", "trialing"]:
		raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Active subscription required")
	return current_user
