"""
Create database tables.
"""

from app.database.database import Base, engine
from app.database import models  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)
