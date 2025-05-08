# database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from typing import Generator

# Load environment variables from .env
load_dotenv()

# Default to SQLite file if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# For SQLite, disable the same-thread check so you can use sessions in FastAPI threads
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Create the engine
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def init_db() -> None:
    """
    Create all tables in the database.
    Called at application startup.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Yield a new Session, and ensure it closes (and rolls back on error).
    """
    with Session(engine) as session:
        yield session
