import os
import tempfile
from uuid import UUID

import ffmpeg
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.firm import Firm
from app.services import transcription

router = APIRouter()


@router.post("/firm/create-profile")
async def create_firm(
    sub: UUID = Depends(get_current_user),
    file: UploadFile = File(...),
    email: str | None = Form(None),        # <-- receive email here
    db: Session = Depends(get_db),
):
    # validate
    ct = file.content_type or ""
    if not (ct.startswith("audio/") or ct.startswith("video/")):
        raise HTTPException(status_code=400, detail="Send audio/* or video/* file")

    src_path = None
    wav_path = None
    try:
        # persist upload
        suffix = os.path.splitext(file.filename or "")[1] or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            src_path = tmp.name
            tmp.write(await file.read())

        # normalize to WAV 16k mono
        wav_path = transcription.to_wav_16k_mono(src_path)

        transcript, info = transcription.transcribe(wav_path)

        # print transcript (as requested)
        print(f"[transcribe] user_sub={sub} lang={info.language} dur={info.duration:.2f}s")
        print(transcript)

        out = transcription.extract_firm_fields(transcript)
        print(out)

        new_firm = Firm(**out, email=email, cognito_sub=sub)
        db.add(new_firm)
        db.commit()
        db.refresh(new_firm)
        return new_firm

    except ffmpeg.Error as e:
        err = e.stderr.decode() if e.stderr else "ffmpeg failed"
        raise HTTPException(status_code=500, detail=f"Audio decode failed: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
    finally:
        for p in (src_path, wav_path):
            if p:
                try: os.remove(p)
                except: pass


@router.get("/firm/exists")
def firm_exists(
    sub: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = db.execute(
        select(Firm.cognito_sub).where(Firm.cognito_sub == sub)
    ).first() is not None
    return {"exists": exists}
