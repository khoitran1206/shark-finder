import os

from dotenv import load_dotenv

load_dotenv()  # loads backend/.env if present


def _list(name: str, default: str) -> list[str]:
    return [v.strip() for v in os.getenv(name, default).split(",") if v.strip()]


# Optional with defaults; secrets (GEMINI_API_KEY) are read where they are used.
DATABASE_URL = os.getenv("DATABASE_URL")  # unset -> local SQLite (see app/database.py)
CORS_ORIGINS = _list("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
WHISPER_SIZE = os.getenv("WHISPER_SIZE", "small")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Public Cognito identifiers (not secrets). Defaults are the current pool; override per environment.
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-2")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "us-east-2_PhoO99PTx")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "3ipsjhg4ulpgbjfmb6nabvuml7")
