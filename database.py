# database.py

import os
from sqlmodel import create_engine, SQLModel, Session
from typing import Generator

# Read the database URL from environment (fallback to SQLite file)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./book_exchange.db")

# Create the SQLModel engine
engine = create_engine(DATABASE_URL, echo=True)

def init_db() -> None:
    """
    Initialize the database.
    Creates all tables defined on the SQLModel metadata.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Provide a transactional session for FastAPI dependencies.
    Yields:
        Session: a SQLModel session connected to the engine.
    """
    with Session(engine) as session:
        yield session
