import os
from datetime import timedelta, datetime, timezone
from typing import Annotated
from passlib.context import CryptContext

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.handlers.des_crypt import bigcrypt
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    is_active: bool = Field(default=True)
    role: str = Field(default="user")
    date_joined: datetime = Field(default=datetime.now(timezone.utc))

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

@router.post("/register")
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







