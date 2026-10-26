import time
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwk, jwt

from app import auth

KID = "test-kid"
SUB = uuid.uuid4()


def _make_key():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_jwk = jwk.construct(private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ), "RS256").to_dict()
    public_jwk["kid"] = KID
    return pem, public_jwk


PRIVATE_PEM, PUBLIC_JWK = _make_key()
OTHER_PEM, _ = _make_key()

app = FastAPI()


@app.get("/me")
def me(user: uuid.UUID = Depends(auth.get_current_user)):
    return {"sub": str(user)}


client = TestClient(app)


@pytest.fixture(autouse=True)
def _trusted_jwks(monkeypatch):
    monkeypatch.setattr(auth, "_get_key", lambda kid, force_refresh=False: PUBLIC_JWK if kid == KID else None)


def _token(pem=PRIVATE_PEM, **overrides):
    claims = {
        "sub": str(SUB),
        "iss": auth.ISSUER,
        "client_id": auth.CLIENT_ID,
        "token_use": "access",
        "exp": int(time.time()) + 300,
        **overrides,
    }
    claims = {k: v for k, v in claims.items() if v is not None}
    return jwt.encode(claims, pem, algorithm="RS256", headers={"kid": KID})


def _get(token):
    return client.get("/me", headers={"Authorization": f"Bearer {token}"})


def test_valid_token_returns_sub():
    r = _get(_token())
    assert r.status_code == 200
    assert r.json() == {"sub": str(SUB)}


def test_missing_header_rejected():
    assert client.get("/me").status_code == 401


def test_forged_signature_rejected():
    assert _get(_token(pem=OTHER_PEM)).status_code == 401


def test_unsigned_alg_none_rejected():
    import base64, json
    b64 = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
    forged = f"{b64({'alg': 'none', 'kid': KID})}.{b64({'sub': str(SUB)})}."
    assert _get(forged).status_code == 401


def test_expired_rejected():
    assert _get(_token(exp=int(time.time()) - 10)).status_code == 401


def test_wrong_issuer_rejected():
    assert _get(_token(iss="https://evil.example.com")).status_code == 401


def test_wrong_client_rejected():
    assert _get(_token(client_id="someone-else")).status_code == 401


def test_id_token_rejected():
    assert _get(_token(token_use="id")).status_code == 401
