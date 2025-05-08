# routes/exchanges.py

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models import Exchange, ExchangeStatus, Family, Book
from security import get_current_active_user

# All endpoints under /exchanges require an authenticated, active user
router = APIRouter(
    tags=["exchanges"],
    redirect_slashes=False,
    dependencies=[Depends(get_current_active_user)],
)


class ExchangeCreate(BaseModel):
    """
    Schema for creating a new exchange request.
    """
    proposer_family_id: int
    receiver_family_id: int
    offered_book_id: int
    requested_book_id: int


class ExchangeRead(BaseModel):
    """
    Schema for reading exchange data.
    """
    id: int
    proposer_family_id: int
    receiver_family_id: int
    offered_book_id: int
    requested_book_id: int
    status: ExchangeStatus
    created_at: datetime
    updated_at: datetime


class ExchangeUpdate(BaseModel):
    """
    Schema for updating only the status of an existing exchange.
    """
    status: ExchangeStatus


@router.get("", response_model=List[ExchangeRead])
def list_exchanges(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    GET /exchanges
    Return a paginated list of all exchanges.
    """
    statement = select(Exchange).offset(skip).limit(limit)
    return session.exec(statement).all()


@router.post("", response_model=ExchangeRead, status_code=status.HTTP_201_CREATED)
def create_exchange(
    *,
    exchange_in: ExchangeCreate,
    session: Session = Depends(get_session),
):
    """
    POST /exchanges
    Create a new exchange request between two families for two books.
    """
    # Validate that both families exist
    if not session.get(Family, exchange_in.proposer_family_id) or not session.get(
        Family, exchange_in.receiver_family_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or both family IDs are invalid.",
        )

    # Validate that both books exist
    if not session.get(Book, exchange_in.offered_book_id) or not session.get(
        Book, exchange_in.requested_book_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or both book IDs are invalid.",
        )

    exch = Exchange(
        proposer_family_id=exchange_in.proposer_family_id,
        receiver_family_id=exchange_in.receiver_family_id,
        offered_book_id=exchange_in.offered_book_id,
        requested_book_id=exchange_in.requested_book_id,
        status=ExchangeStatus.pending,
    )
    session.add(exch)
    session.commit()
    session.refresh(exch)
    return exch


@router.get("/{exchange_id}", response_model=ExchangeRead)
def get_exchange(
    *,
    exchange_id: int,
    session: Session = Depends(get_session),
):
    """
    GET /exchanges/{exchange_id}
    Retrieve a single exchange by its ID.
    """
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found.",
        )
    return exchange


@router.put("/{exchange_id}", response_model=ExchangeRead)
def update_exchange(
    *,
    exchange_id: int,
    exchange_in: ExchangeUpdate,
    session: Session = Depends(get_session),
):
    """
    PUT /exchanges/{exchange_id}
    Update the status of an existing exchange.
    """
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found.",
        )

    exchange.status = exchange_in.status
    exchange.updated_at = datetime.utcnow()
    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return exchange


@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exchange(
    *,
    exchange_id: int,
    session: Session = Depends(get_session),
):
    """
    DELETE /exchanges/{exchange_id}
    Delete an exchange request by its ID.
    """
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found.",
        )
    session.delete(exchange)
    session.commit()
    return
