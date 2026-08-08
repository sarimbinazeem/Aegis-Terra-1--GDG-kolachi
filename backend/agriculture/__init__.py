from .database import initialize_database
from .seed import seed_database


def initialize_agricultural_knowledge_base() -> None:
    initialize_database()
    seed_database()