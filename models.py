# book_exchange_app/models.py
"""
Database models for Book Exchange App using SQLModel.
Defines data structures: Family, User, Book, and Exchange.
Includes fields for secure authentication and LOPDGDD/RGPD compliance.
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


def get_prefix() -> str:
    """
    Helper for consistent foreign key naming (unused placeholder).
    """
    return ""


class Family(SQLModel, table=True):
    """
    Represents a family group within the application.
    Each family can have multiple users and exchanges.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, description="Family name or group identifier")

    # Relationships
    users: List["User"] = Relationship(back_populates="family")
    exchanges: List["Exchange"] = Relationship(back_populates="family")


class User(SQLModel, table=True):
    """
    Represents an individual user belonging to a family, with secure credential storage.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False, description="Username or alias for login")
    email: str = Field(index=True, unique=True, nullable=False, description="Contact email for notifications")
    hashed_password: str = Field(nullable=False, description="Password hash for authentication")
    is_active: bool = Field(default=True, description="Flag to mark active/inactive users for compliance")
    family_id: Optional[int] = Field(foreign_key="family.id", nullable=False, description="Reference to the user's family")

    # Relationships
    family: Optional[Family] = Relationship(back_populates="users")


class Book(SQLModel, table=True):
    """
    Represents a textbook or reading book available for exchange.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False, description="Book title")
    author: Optional[str] = Field(default=None, index=True, description="Book author")
    grade: Optional[int] = Field(default=None, description="School grade or level")
    isbn: Optional[str] = Field(default=None, unique=True, index=True, description="International Standard Book Number")
    added_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when book was added")
    owner_id: Optional[int] = Field(foreign_key="user.id", nullable=False, description="User who owns the book")

    # Relationships
    owner: Optional[User] = Relationship()
    exchanges: List["Exchange"] = Relationship(back_populates="book")


class Exchange(SQLModel, table=True):
    """
    Represents a proposed or completed exchange between two families for a specific book.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id", nullable=False, description="Book to be exchanged")
    family_id: int = Field(foreign_key="family.id", nullable=False, description="Family proposing the exchange")
    to_family_id: int = Field(foreign_key="family.id", nullable=False, description="Family receiving the proposal")
    status: str = Field(default="pending", description="Exchange status: pending, accepted, declined, completed")
    requested_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when exchange requested")
    responded_at: Optional[datetime] = Field(default=None, description="Timestamp when exchange was responded to")

    # Relationships
    book: "Book" = Relationship(back_populates="exchanges")
    family: "Family" = Relationship(back_populates="exchanges")
    to_family: "Family" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Exchange.to_family_id == Family.id"}
    )
