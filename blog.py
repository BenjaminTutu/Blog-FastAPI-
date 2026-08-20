from datetime import date

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from database import SessionLocal
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from models import *


router = APIRouter(
    prefix="/blog",
    tags=["blog"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency =  Annotated[Session, Depends(get_db)]

class AuthorResponse(BaseModel):
    username: str
    id: int

class PostResponse(BaseModel):
    title: str = Field(min_length=3)
    body: str = Field(min_length=3, max_length=200)
    slug: str = Field(min_length=1)
    date_posted: date = Field(default=datetime.date.today)
    author: AuthorResponse

    model_config = ConfigDict(from_attributes=True)

@router.get("/posts")
async def get_posts(db:db_dependency):
    posts = db.query(Post).all()
    return posts


@router.post("/create-post", response_model=PostResponse)
async def create_post(db:db_dependency, post: PostResponse):
    new_post = Post(
        title=post.title,
        body=post.body,
        slug=post.slug,
        date_posted=post.date_posted
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post





