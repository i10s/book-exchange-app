# models.py

from typing import Optional, List
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship


class Family(SQLModel, table=True):
    """
    Represents a family (i.e. a user group) in the school community.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

    # Back-reference to this family’s books and exchanges
    books: List["Book"] = Relationship(back_populates="owner")
    exchanges_proposed: List["Exchange"] = Relationship(
        back_populates="proposer_family",
        sa_relationship_kwargs={"primaryjoin": "Family.id==Exchange.proposer_family_id"}
    )
    exchanges_received: List["Exchange"] = Relationship(
        back_populates="receiver_family",
        sa_relationship_kwargs={"primaryjoin": "Family.id==Exchange.receiver_family_id"}
    )


class User(SQLModel, table=True):
    """
    Represents an individual user who can log in to the system.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = True


class Book(SQLModel, table=True):
    """
    Represents a book owned by a family.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    grade: Optional[int] = None
    isbn: Optional[str] = None

    owner_id: int = Field(foreign_key="family.id")
    owner: Optional[Family] = Relationship(back_populates="books")


class ExchangeStatus(str, Enum):
    """
    Defines the lifecycle states of a book exchange proposal.
    """
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class Exchange(SQLModel, table=True):
    """
    Represents a proposal to exchange one book for another between two families.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    proposer_family_id: int = Field(foreign_key="family.id")
    receiver_family_id: int = Field(foreign_key="family.id")

    offered_book_id: int = Field(foreign_key="book.id")
    requested_book_id: int = Field(foreign_key="book.id")

    status: ExchangeStatus = Field(default=ExchangeStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    proposer_family: Optional[Family] = Relationship(
        back_populates="exchanges_proposed",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.proposer_family_id]"}
    )
    receiver_family: Optional[Family] = Relationship(
        back_populates="exchanges_received",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.receiver_family_id]"}
    )
    offered_book: Optional[Book] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Exchange.offered_book_id]"}
    )
    requested_book: Optional[Book] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Exchange.requested_book_id]"}
    )
