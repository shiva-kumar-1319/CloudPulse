import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from shared.config.settings import settings

# Determine DB URL for auth service
DATABASE_URL = os.getenv("AUTH_DB_URL", settings.AUTH_DB_URL)

# Configure engine arguments based on DB type (SQLite vs Postgres)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency that yields a database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create database tables if they do not exist.
    """
    Base.metadata.create_all(bind=engine)
