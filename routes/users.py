# routes/users.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from database import get_session
from models import User
from security import get_password_hash, get_current_active_user

router = APIRouter(
    tags=["users"],
    redirect_slashes=False,
)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    session: Session = Depends(get_session),
):
    """
    POST /users
    (Public) Register a new user.
    """
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed = get_password_hash(user_in.password)
    user = User(username=user_in.username, email=user_in.email, hashed_password=hashed, is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("", response_model=List[UserRead], dependencies=[Depends(get_current_active_user)])
def list_users(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    GET /users
    (Protected) List all users.
    """
    return session.exec(select(User).offset(skip).limit(limit)).all()

@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_active_user)])
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    """
    GET /users/{user_id}
    (Protected) Fetch a single user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_active_user)])
def update_user(
    user_id: int,
    user_in: UserUpdate,
    session: Session = Depends(get_session),
):
    """
    PUT /users/{user_id}
    (Protected) Update a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updates = user_in.dict(exclude_unset=True)
    if "password" in updates:
        updates["hashed_password"] = get_password_hash(updates.pop("password"))
    for field, value in updates.items():
        setattr(user, field, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)])
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    """
    DELETE /users/{user_id}
    (Protected) Remove a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session.delete(user)
    session.commit()
    return
