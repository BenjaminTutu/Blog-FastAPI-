import os
from datetime import timedelta, datetime, timezone, date
from typing import Annotated
from passlib.context import CryptContext

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from database import SessionLocal
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer("/auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: str = Field(min_length=3, max_length=45)
    password: str = Field(min_length=3, max_length=72)
    is_active: bool = Field(default=True)
    role: str = Field(default="user")
    date_joined: datetime = Field(default_factory=date.today)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "john",
                "email": "john@example.com",
                "password": "",
                "is_active": True,
                "role": "user",
                "date_joined": datetime.now(timezone.utc).isoformat()
            }
        }
    )

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db: Session):
    user_model = db.query(User).filter(User.username == username).first()
    if not user_model:
        return False
    if not bcrypt_context.verify(password, user_model.password):
        return False
    return user_model

def create_access_token(username:str, user_id: int, expires_delta: timedelta):
    payload = {
        "sub": username,
        "id": user_id,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="Could not validate credentials")
        return {'id': user_id, 'username': username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.post("/register", response_model=UserCreate, status_code=201)
async def register(user: UserCreate, db:Session = Depends(get_db)):
    user = User(
        username=user.username,
        email=user.email,
        password=bcrypt_context.hash(user.password),
        is_active=user.is_active,
        role=user.role,
        date_joined=user.date_joined,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token, status_code=200)
async def create_access_token_login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db:Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user or not bcrypt_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}







