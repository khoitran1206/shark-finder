import json
from types import SimpleNamespace

import pytest

from app.services import transcription as t


@pytest.mark.parametrize(
    "raw, expected",
    [(2500000, 2500000), ("2.5M", 2500000), ("$500k", 500000), ("3,000,000", 3000000), (None, None), ("n/a", None)],
)
def test_to_int_amount(raw, expected):
    assert t._to_int_amount(raw) == expected


def test_normalizers():
    assert t._normalize_enum("very aggressive", t._RISK_MAP) == "High"
    assert t._normalize_enum("a round", t._STAGE_MAP) == "Series A"
    assert t._normalize_enum("sometimes", t._FREQ_MAP) is None
    assert t._to_bool("willing") is True and t._to_bool("nope") is False and t._to_bool("maybe") is None


def _fake_model(response_text=None, raises=False):
    class FakeModel:
        def __init__(self, *args, **kwargs):
            pass

        def generate_content(self, prompt):
            if raises:
                raise RuntimeError("gemini down")
            return SimpleNamespace(text=response_text)

    return FakeModel


def test_extract_firm_fields_normalizes(monkeypatch):
    reply = {"name": "  Acme  ", "risk_tolerance": "aggressive", "investment_size": "2.5M",
             "years_active": "12 years", "board_seat": "yes", "meeting_frequency": "monthly"}
    monkeypatch.setattr(t.genai, "GenerativeModel", _fake_model(json.dumps(reply)))
    out = t.extract_firm_fields("transcript")
    assert out["name"] == "Acme"
    assert out["risk_tolerance"] == "High"
    assert out["investment_size"] == 2500000
    assert out["years_active"] == 12
    assert out["board_seat"] is True
    assert out["meeting_frequency"] == "Monthly"
    assert out["industry"] is None


def test_extract_firm_fields_falls_back_to_empty_profile(monkeypatch):
    monkeypatch.setattr(t.genai, "GenerativeModel", _fake_model(raises=True))
    out = t.extract_firm_fields("transcript")
    assert out["name"] is None and all(v is None for v in out.values())
