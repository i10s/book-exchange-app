# routes/auth.py

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select, or_

from database import get_session
from security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)
from models import User, Family

router = APIRouter(tags=["auth"])

# OAuth2 flow will POST credentials here to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    access_token: str
    token_type: str
    family_id: int


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account and family",
)
def register_user(
    request: RegisterRequest,
    session: Session = Depends(get_session),
):
    """
    Register a new user *and* a family record.
    Fails if username or email is already taken.
    Returns a JWT plus the new family_id.
    """
    # 1) Prevent duplicate username OR email
    dup_stmt = select(User).where(
        or_(User.username == request.username, User.email == request.email)
    )
    if session.exec(dup_stmt).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # 2) Create the User
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # 3) Create the Family (for book ownership grouping)
    family = Family(
        name=f"{request.username} Family",
        email=request.email,
    )
    session.add(family)
    session.commit()
    session.refresh(family)

    # 4) Issue a JWT
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.username}, expires_delta=expires)

    return {
        "access_token": token,
        "token_type": "bearer",
        "family_id": family.id,
    }


@router.post("/token", response_model=Token, summary="Obtain JWT token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Exchange username and password for a JWT access token.
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=expires_delta
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> User:
    """
    Decode and verify the JWT, then return the corresponding User.
    Raises 401 if the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    stmt = select(User).where(User.username == username)
    user = session.exec(stmt).one_or_none()
    if user is None:
        raise credentials_exception

    return user
