
"""
Database configuration.

SQLite database for local persistence.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = "sqlite:///./app/aegis_terra.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    Provide a database session to API routes.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
