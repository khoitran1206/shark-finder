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


@pytest.fixture(autouse=True)
def _no_gemini_setup(monkeypatch):
    monkeypatch.setattr(t, "_configure_gemini", lambda: None)


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


def test_import_does_not_load_models_or_need_a_key(monkeypatch):
    # conftest removed GEMINI_API_KEY before importing the app; nothing was loaded either.
    assert t.get_whisper_model.cache_info().currsize == 0


def test_missing_gemini_key_fails_on_use_not_on_import(monkeypatch):
    monkeypatch.undo()
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    t._configure_gemini.cache_clear()
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        t.extract_firm_fields("transcript")


def test_whisper_model_loaded_once_with_configured_size(monkeypatch):
    calls = []
    monkeypatch.setattr(t.faster_whisper, "WhisperModel", lambda *a, **k: calls.append((a, k)) or object())
    t.get_whisper_model.cache_clear()
    first, second = t.get_whisper_model(), t.get_whisper_model()
    assert first is second and len(calls) == 1
    assert calls[0][0][0] == t.WHISPER_SIZE
    t.get_whisper_model.cache_clear()
