import os
import tempfile

# Must run before any `app` import: use a throwaway SQLite file and fake Gemini key.
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["GEMINI_API_KEY"] = "test-key"

import faster_whisper  # noqa: E402

# Avoid downloading/loading a real Whisper model at import time.
faster_whisper.WhisperModel = lambda *args, **kwargs: object()
