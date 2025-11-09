from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path
import warnings


# Try to load .env from working dir first, then from the package folder.
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    package_env = Path(__file__).resolve().parent / ".env"
    if package_env.exists():
        load_dotenv(package_env)
        DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Provide a safe fallback for local development so create_engine doesn't
    # receive None. In production you should set DATABASE_URL to your
    # PostgreSQL (or other) DSN. We default to a local SQLite file.
    warnings.warn(
        "DATABASE_URL not set. Falling back to a local SQLite database at './dev.db'. "
        "Set the DATABASE_URL environment variable or create a backend/app/.env file to configure a real DB.",
        RuntimeWarning,
    )
    DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parent.parent / 'dev.db'}"

# Create the engine (will raise for invalid URLs)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency (route içinde kullanmak için)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
