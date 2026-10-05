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
    db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
elif db_url.startswith("postgresql://") and "+pg8000" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)

# Configure engine connect_args for SQLite
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(db_url, connect_args=connect_args)
    # Test connection
    with engine.connect() as conn:
        pass
    logger.info(f"Database engine initialized successfully.")
except Exception as e:
    logger.warning(f"Database connection to {db_url} failed ({e}). Initializing SQLite engine at sqlite:///./schemesathi.db.")
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
