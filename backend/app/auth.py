import os
import time
from uuid import UUID

import httpx
from fastapi import Header, HTTPException
from jose import JWTError, jwt

# Defaults are the public identifiers of the existing Cognito pool; override via env.
REGION = os.getenv("COGNITO_REGION", "us-east-2")
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "us-east-2_PhoO99PTx")
CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "3ipsjhg4ulpgbjfmb6nabvuml7")

ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"
JWKS_TTL_SECONDS = 3600

_jwks: dict = {"keys": [], "fetched_at": 0.0}


def _get_key(kid: str, force_refresh: bool = False) -> dict | None:
    if force_refresh or time.time() - _jwks["fetched_at"] > JWKS_TTL_SECONDS:
        try:
            resp = httpx.get(JWKS_URL, timeout=5)
            resp.raise_for_status()
            _jwks["keys"] = resp.json()["keys"]
            _jwks["fetched_at"] = time.time()
        except Exception:
            raise HTTPException(status_code=503, detail="Auth keys unavailable")
    return next((k for k in _jwks["keys"] if k.get("kid") == kid), None)


def get_current_user(authorization: str | None = Header(None)) -> UUID:
    """FastAPI dependency: verify the Cognito access token and return the user's sub."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing/invalid Authorization header")
    token = authorization.split(" ", 1)[1]

    try:
        kid = jwt.get_unverified_header(token).get("kid")
        # A key rotation may leave an unknown kid in our cache; refresh once before rejecting.
        key = _get_key(kid) or _get_key(kid, force_refresh=True)
        if key is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        # Cognito access tokens carry no `aud`; client_id is checked below instead.
        claims = jwt.decode(
            token, key, algorithms=["RS256"], issuer=ISSUER, options={"verify_aud": False}
        )
        if claims.get("token_use") != "access" or claims.get("client_id") != CLIENT_ID:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UUID(claims["sub"])
    except HTTPException:
        raise
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
