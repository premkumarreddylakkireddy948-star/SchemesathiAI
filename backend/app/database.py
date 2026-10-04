import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# Enforce no C extension DLL loading issues on Windows
os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Configure engine connect_args for SQLite (development mode only)
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

if settings.is_production:
    if db_url.startswith("sqlite"):
        raise RuntimeError("PRODUCTION CONFIGURATION ERROR: SQLite is not permitted in production mode. Set a valid PostgreSQL DATABASE_URL.")
    try:
        engine = create_engine(db_url)
        logger.info(f"Production PostgreSQL engine initialized successfully.")
    except Exception as e:
        raise RuntimeError(f"PRODUCTION DATABASE ERROR: Failed to connect to production PostgreSQL database at {db_url}: {e}")
else:
    # Development mode: allow fallback to local SQLite if PostgreSQL is unavailable
    try:
        engine = create_engine(db_url, connect_args=connect_args)
    except Exception as e:
        logger.warning(f"Development DB connect failed ({e}), falling back to local SQLite at sqlite:///./schemesathi.db.")
        db_url = "sqlite:///./schemesathi.db"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
