from typing import Dict, Any
import time
import jwt
from jwt import PyJWKClient
from functools import lru_cache
from app.config import settings

_JWKS_TTL_SECONDS = 300
_CLOCK_SKEW_LEEWAY = 60

@lru_cache(maxsize=1)
def _jwks_client(domain: str, _bucket: int) -> PyJWKClient:
	return PyJWKClient(f"https://{domain}/.well-known/jwks.json")

def verify_auth0_id_token(id_token: str) -> Dict[str, Any]:
	if not settings.auth0_domain or not settings.auth0_client_id:
		raise ValueError("Auth0 not configured")
	client = _jwks_client(settings.auth0_domain, int(time.time()/_JWKS_TTL_SECONDS))
	key = client.get_signing_key_from_jwt(id_token).key
	decoded = jwt.decode(
		id_token,
		key,
		algorithms=["RS256"],
		audience=settings.auth0_client_id,
		issuer=f"https://{settings.auth0_domain}/",
		leeway=_CLOCK_SKEW_LEEWAY,
		options={"verify_at_hash": False},
	)
	if decoded.get("iss") != f"https://{settings.auth0_domain}/":
		raise jwt.InvalidIssuerError("Invalid issuer")
	return decoded 