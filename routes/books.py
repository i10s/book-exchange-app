# routes/books.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models import Book
from security import get_current_active_user

# All /books endpoints now require a valid, active JWT user
router = APIRouter(
    redirect_slashes=False,
    dependencies=[Depends(get_current_active_user)]
)

class BookCreate(BaseModel):
    title: str
    author: str
    grade: Optional[int] = None
    isbn: Optional[str] = None
    owner_id: int

class BookRead(BaseModel):
    id: int
    title: str
    author: str
    grade: Optional[int]
    isbn: Optional[str]
    owner_id: int

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    grade: Optional[int] = None
    isbn: Optional[str] = None
    owner_id: Optional[int] = None

@router.get("", response_model=List[BookRead])
def list_books(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    GET /books
    """
    return session.exec(select(Book).offset(skip).limit(limit)).all()

@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: BookCreate,
    session: Session = Depends(get_session),
):
    """
    POST /books
    """
    book = Book(**book_in.dict())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: Session = Depends(get_session)):
    """
    GET /books/{book_id}
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    book_in: BookUpdate,
    session: Session = Depends(get_session),
):
    """
    PUT /books/{book_id}
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    updates = book_in.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(book, field, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    """
    DELETE /books/{book_id}
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    session.delete(book)
    session.commit()
    return
