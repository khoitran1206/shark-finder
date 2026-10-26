import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.services import transcription
from main import app

INVESTOR_ID = uuid.uuid4()
FIRM_ID = uuid.uuid4()
current_user = {"id": INVESTOR_ID}

app.dependency_overrides[get_current_user] = lambda: current_user["id"]
client = TestClient(app)


def as_user(user_id):
    current_user["id"] = user_id


def test_routes_registered_once():
    paths = [(m, r.path) for r in app.routes if hasattr(r, "methods") for m in r.methods - {"HEAD", "OPTIONS"}]
    assert len(paths) == len(set(paths))
    assert ("POST", "/investor/create-profile") in paths
    assert ("POST", "/firm/create-profile") in paths
    assert ("GET", "/firms/{firm_id}/matching-investors") in paths
    assert ("GET", "/investors/{investor_id}/matching-firms") in paths
    assert ("GET", "/investors/") not in paths and ("GET", "/firms/") not in paths


def test_investor_flow_and_match_ownership():
    as_user(INVESTOR_ID)
    assert client.get("/investor/exists").json() == {"exists": False}

    body = {"name": "Ada", "email": "ada@example.com", "risk_tolerance": "Medium", "industry": "Fintech"}
    assert client.post("/investor/create-profile", json=body).status_code == 200
    assert client.post("/investor/create-profile", json=body).status_code == 400
    assert client.get("/investor/exists").json() == {"exists": True}

    assert client.get(f"/investors/{uuid.uuid4()}/matching-firms").status_code == 403
    assert client.get(f"/investors/{INVESTOR_ID}/matching-firms").status_code == 200


def test_firm_flow_and_matching(monkeypatch):
    fields = {
        "name": "Acme", "risk_tolerance": "Medium", "industry": "Fintech", "years_active": 3,
        "num_investments": None, "board_seat": None, "location": None, "investment_size": None,
        "investment_stage": None, "follow_on_rate": None, "rate_of_return": None,
        "success_rate": None, "reserved_capital": None, "meeting_frequency": None,
    }
    monkeypatch.setattr(transcription, "to_wav_16k_mono", lambda p: p)
    monkeypatch.setattr(transcription, "transcribe", lambda p: ("pitch", SimpleNamespace(language="en", duration=1.0)))
    monkeypatch.setattr(transcription, "extract_firm_fields", lambda t: dict(fields))

    as_user(FIRM_ID)
    r = client.post(
        "/firm/create-profile",
        files={"file": ("pitch.wav", b"fake", "audio/wav")},
        data={"email": "acme@example.com"},
    )
    assert r.status_code == 200, r.text
    assert client.get("/firm/exists").json() == {"exists": True}
    assert client.post("/firm/create-profile", files={"file": ("a.txt", b"x", "text/plain")}).status_code == 400

    matches = client.get(f"/firms/{FIRM_ID}/matching-investors").json()
    assert matches and matches[0]["investor"]["name"] == "Ada"
    assert matches[0]["match_score"] == 15  # industry (5) + risk (10)

    as_user(INVESTOR_ID)
    firms = client.get(f"/investors/{INVESTOR_ID}/matching-firms").json()
    assert firms and firms[0]["firm"]["name"] == "Acme"
