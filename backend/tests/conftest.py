import os
import tempfile

# Must run before any `app` import: use a throwaway SQLite file. No Gemini key and no
# Whisper model are set up on purpose: importing the app must work without them.
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ.pop("GEMINI_API_KEY", None)
