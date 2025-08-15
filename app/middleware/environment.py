"""
Environment validation middleware (minimal)
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger(__name__)

class EnvironmentValidationMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		return await call_next(request)