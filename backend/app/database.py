from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from app.config import DATABASE_URL

# If DATABASE_URL is unset, fall back to local sqlite for dev
if not DATABASE_URL:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sqlite_path = os.path.join(BASE_DIR, "./dev.db")
    DATABASE_URL = f"sqlite:///{sqlite_path}"

# For sqlite we need connect_args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Move get_db here
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()