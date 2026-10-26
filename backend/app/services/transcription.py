import json
import os
import re
from functools import lru_cache
from typing import Any, Dict, Optional

import ffmpeg
import google.generativeai as genai
import faster_whisper

from app.config import GEMINI_MODEL, WHISPER_SIZE

# --- transcription + firm profile extraction ---


@lru_cache(maxsize=1)
def _configure_gemini() -> None:
    """Configure Gemini on first use so the app can start (and be tested) without a key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)


@lru_cache(maxsize=1)
def get_whisper_model():
    """Load the Whisper model on first use (it is large and slow to load)."""
    # device="auto" uses GPU if available; compute_type="auto" picks best precision
    return faster_whisper.WhisperModel(WHISPER_SIZE, device="auto", compute_type="auto")

# --- lightweight normalizers (inline; no external deps) ---
_RISK_MAP = {
    "low": "Low", "conservative": "Low", "defensive": "Low",
    "medium": "Medium", "moderate": "Medium", "balanced": "Medium",
    "high": "High", "aggressive": "High", "very high": "High"
}
_STAGE_MAP = {
    "pre seed": "Pre-seed", "pre-seed": "Pre-seed", "preseed": "Pre-seed",
    "seed": "Seed",
    "series a": "Series A", "a round": "Series A",
    "series b": "Series B+", "b round": "Series B+", "series b+": "Series B+", "growth": "Series B+",
    "public": "Public", "ipo": "Public", "listed": "Public",
}

_FREQ_MAP = {"weekly": "Weekly", "monthly": "Monthly", "quarterly": "Quarterly"}

def _to_bool(val: Any) -> Optional[bool]:
    if isinstance(val, bool): return val
    if val is None: return None
    t = str(val).strip().lower()
    if t in {"yes","true","y","1","take","willing","open"}: return True
    if t in {"no","false","n","0","not","nope"}: return False
    return None

def _normalize_enum(val: Optional[str], mapping: Dict[str, str]) -> Optional[str]:
    if not val: return None
    t = val.strip().lower()
    # exact then "contains"
    if t in mapping: return mapping[t]
    for k,v in mapping.items():
        if k in t: return v
    return None

_num_token = re.compile(r"(\d+(?:\.\d+)?)\s*([kmbKMB])?$")

def _to_int_amount(val: Any) -> Optional[int]:
    """
    Accepts 2500000, "2.5M", "$500k", "3,000,000" -> int (assumed dollars or your unit)
    """
    if val is None: return None
    if isinstance(val, (int, float)): return int(round(val))
    s = str(val).strip().replace(",", "").replace("$","")
    m = _num_token.fullmatch(s)
    if m:
        num = float(m.group(1))
        suf = (m.group(2) or "").lower()
        if suf == "k": num *= 1_000
        elif suf == "m": num *= 1_000_000
        elif suf == "b": num *= 1_000_000_000
        return int(round(num))
    # fallback: first plain integer in string
    m2 = re.search(r"\b\d{1,9}\b", s)
    return int(m2.group(0)) if m2 else None

_int_token = re.compile(r"\b\d{1,4}\b")

def _to_int(val: Any, lo: int = 0, hi: int = 1_000_000) -> Optional[int]:
    if val is None: return None
    try:
        iv = int(val)
        return iv if lo <= iv <= hi else None
    except:
        s = str(val)
        m = _int_token.search(s)
        if not m: return None
        iv = int(m.group(0))
        return iv if lo <= iv <= hi else None


def to_wav_16k_mono(src_path: str) -> str:
    """Convert any audio/video to 16 kHz mono WAV for Whisper."""
    out_path = src_path + ".wav"
    (
        ffmpeg
        .input(src_path)
        .output(out_path, ac=1, ar="16000", format="wav", loglevel="error")
        .overwrite_output()
        .run()
    )
    return out_path


def transcribe(wav_path: str):
    """Transcribe a 16 kHz mono WAV. Returns (transcript, info)."""
    segments, info = get_whisper_model().transcribe(
        wav_path,
        language=None,        # auto-detect
        vad_filter=True,      # helps on noisy/pauses
        beam_size=5,          # decent accuracy/latency tradeoff
    )
    return "".join(seg.text for seg in segments).strip(), info


def extract_firm_fields(transcript: str) -> Dict[str, Any]:
    """Ask Gemini for firm characteristics in the transcript and normalise them."""
    sys = (
    "Task: Extract firm characteristics from a startup pitch transcript.\n"
    "Return STRICT JSON with these keys ONLY:\n"
    "name, risk_tolerance, industry, years_active, num_investments, board_seat, "
    "location, investment_size, investment_stage, follow_on_rate, rate_of_return, "
    "success_rate, reserved_capital, meeting_frequency.\n"
    "Rules:\n"
    "- If not stated, output null.\n"
    "- Do NOT guess.\n"
    "- risk_tolerance ∈ {Low, Medium, High} or null.\n"
    "- investment_stage ∈ {Pre-seed, Seed, Series A, Series B+, Public} or null.\n"
    "- meeting_frequency ∈ {Weekly, Monthly, Quarterly} or null.\n"
    "- years_active, num_investments: integers or null.\n"
    "- investment_size: integer (e.g., 2500000) or null.\n"
    "- board_seat, follow_on_rate: booleans or null.\n"
    "- rate_of_return, success_rate, reserved_capital: free-form strings if present.\n"
    "Return ONLY JSON. No prose, no markdown."
    )
    prompt = f"Transcript:\n```\n{transcript}\n```\nJSON only."

    _configure_gemini()
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        system_instruction=sys,
        generation_config={"temperature": 0.1, "response_mime_type": "application/json"},
    )

    try:
        resp = model.generate_content(prompt)
        raw = (resp.text or "").strip()
        data = json.loads(raw)
    except Exception:
        # hard fallback: empty skeleton
        data = {}

    # 2) Ensure all keys exist
    out: Dict[str, Any] = {
        "name":                data.get("name"),
        "risk_tolerance":      data.get("risk_tolerance"),
        "industry":            data.get("industry"),
        "years_active":        data.get("years_active"),
        "num_investments":     data.get("num_investments"),
        "board_seat":          data.get("board_seat"),
        "location":            data.get("location"),
        "investment_size":     data.get("investment_size"),
        "investment_stage":    data.get("investment_stage"),
        "follow_on_rate":      data.get("follow_on_rate"),
        "rate_of_return":      data.get("rate_of_return"),
        "success_rate":        data.get("success_rate"),
        "reserved_capital":    data.get("reserved_capital"),
        "meeting_frequency":   data.get("meeting_frequency"),
    }

    # 3) Normalize types/enums
    out["risk_tolerance"]   = _normalize_enum(out["risk_tolerance"], _RISK_MAP)
    out["investment_stage"] = _normalize_enum(out["investment_stage"], _STAGE_MAP)
    out["meeting_frequency"]= _normalize_enum(out["meeting_frequency"], _FREQ_MAP)

    out["years_active"]     = _to_int(out["years_active"], lo=0, hi=200)
    out["num_investments"]  = _to_int(out["num_investments"], lo=0, hi=1_000_000)
    out["investment_size"]  = _to_int_amount(out["investment_size"])

    out["board_seat"]       = _to_bool(out["board_seat"])
    out["follow_on_rate"]   = _to_bool(out["follow_on_rate"])

    # 4) Minimal name cleanup
    if isinstance(out["name"], str):
        out["name"] = out["name"].strip() or None


    return out
