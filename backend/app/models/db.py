# backend/app/models/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)
Base = declarative_base()

def init_engine():
    """
    Initialize SQLAlchemy engine and bind SessionLocal.
    POSTGRES_URI examples:
      - postgresql+psycopg2://postgres:postgres@db:5432/sls
      - sqlite:///./sls.db  (fallback)
    """
    global engine, SessionLocal
    url = os.getenv("POSTGRES_URI", "sqlite:///./sls.db")
    engine = create_engine(url, future=True)
    SessionLocal.configure(bind=engine)

def create_all():
    # import models to register metadata before create_all
    from app.models import orm  # noqa: F401
    Base.metadata.create_all(bind=engine)

# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
