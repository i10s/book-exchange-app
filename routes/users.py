# book_exchange_app/routers/users.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select, SQLModel

from ..database import get_session
from ..models import User
from ..security import get_password_hash

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/", response_model=List[UserRead])
def read_users(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve a paginated list of users.
    - skip: number of records to skip
    - limit: maximum number of records to return
    """
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    *,
    session: Session = Depends(get_session),
    user_id: int,
):
    """
    Retrieve a single user by ID.
    Raises 404 if not found.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    *,
    session: Session = Depends(get_session),
    user_in: UserCreate,
):
    """
    Create a new user.
    - Ensures the email is unique
    - Hashes the provided password
    """
    # Check for existing email
    existing = session.exec(
        select(User).where(User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    *,
    session: Session = Depends(get_session),
    user_id: int,
    user_in: UserUpdate,
):
    """
    Update an existing user.
    - Only supplied fields are modified
    - If password is provided, it is re-hashed
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    updates = user_in.dict(exclude_unset=True)
    if "password" in updates:
        updates["hashed_password"] = get_password_hash(updates.pop("password"))

    for field, value in updates.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    session: Session = Depends(get_session),
    user_id: int,
):
    """
    Delete a user by ID.
    Raises 404 if the user does not exist.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    session.delete(user)
    session.commit()
    return
