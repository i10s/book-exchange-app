# book_exchange_app/routers/books.py
"""
Router for CRUD operations on books in the Book Exchange App.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from ..database import get_session
from ..models import Book

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

@router.get("/", response_model=List[Book])
async def read_books(
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    """
    Retrieve a list of books with optional pagination.
    """
    statement = select(Book).limit(limit).offset(offset)
    results = session.exec(statement)
    return results.all()

@router.get("/{book_id}", response_model=Book)
async def read_book(
    book_id: int,
    session: Session = Depends(get_session),
):
    """
    Retrieve a single book by its ID.
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: Book,
    session: Session = Depends(get_session),
):
    """
    Create a new book entry.
    """
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: int,
    updated: Book,
    session: Session = Depends(get_session),
):
    """
    Update an existing book by ID.
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    book_data = updated.dict(exclude_unset=True)
    for key, value in book_data.items():
        setattr(book, key, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    session: Session = Depends(get_session),
):
    """
    Delete a book by ID.
    """
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    session.delete(book)
    session.commit()
    return None
