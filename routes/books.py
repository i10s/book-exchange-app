# routes/books.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models import Book
from security import get_current_active_user

# All endpoints under /books require a valid, active JWT user
router = APIRouter(
    prefix="/books",
    tags=["books"],
    redirect_slashes=False,
    dependencies=[Depends(get_current_active_user)],
)


class BookCreate(BaseModel):
    """
    Schema for creating a new book.
    """
    title: str
    author: str
    grade: Optional[int] = None
    isbn: Optional[str] = None
    owner_id: int


class BookRead(BaseModel):
    """
    Schema for reading book data.
    """
    id: int
    title: str
    author: str
    grade: Optional[int]
    isbn: Optional[str]
    owner_id: int


class BookUpdate(BaseModel):
    """
    Schema for updating book fields.
    Only non-null fields will be updated.
    """
    title: Optional[str] = None
    author: Optional[str] = None
    grade: Optional[int] = None
    isbn: Optional[str] = None
    owner_id: Optional[int] = None


@router.get("", response_model=List[BookRead])
def list_books(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    GET /books
    Return a paginated list of books.
    """
    statement = select(Book).offset(skip).limit(limit)
    return session.exec(statement).all()


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(
    *,
    book_in: BookCreate,
    session: Session = Depends(get_session),
):
    """
    POST /books
    Create a new book.
    """
    book = Book(**book_in.dict())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.get("/{book_id}", response_model=BookRead)
def get_book(
    *,
    book_id: int,
    session: Session = Depends(get_session),
):
    """
    GET /books/{book_id}
    Retrieve a book by its ID.
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book


@router.put("/{book_id}", response_model=BookRead)
def update_book(
    *,
    book_id: int,
    book_in: BookUpdate,
    session: Session = Depends(get_session),
):
    """
    PUT /books/{book_id}
    Update an existing book. Only provided fields will be changed.
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    updates = book_in.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(book, field, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    *,
    book_id: int,
    session: Session = Depends(get_session),
):
    """
    DELETE /books/{book_id}
    Delete a book by its ID.
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    session.delete(book)
    session.commit()
    return
