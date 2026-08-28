from datetime import date

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from typing import Annotated, List
from pydantic import BaseModel, Field, ConfigDict
from models import *
from auth import get_current_user


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

    model_config = ConfigDict(from_attributes=True)

class CommentsResponse(BaseModel):
    comment_body: str = Field(min_length=3)
    comment_author: AuthorResponse

    model_config = ConfigDict(from_attributes=True)

class PostCreate(BaseModel):
    title: str
    body: str
    slug: str
    date_posted: date = Field(default_factory=date.today)


class PostResponse(BaseModel):
    title: str = Field(min_length=3)
    body: str = Field(min_length=3, max_length=200)
    slug: str = Field(min_length=1)
    date_posted: date = Field(default_factory=date.today)
    comments: List[CommentsResponse]

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
   comment_body: str

   model_config = ConfigDict(from_attributes=True)

class PostUpdate(BaseModel):
    title: str
    body: str
    slug: str
    date_posted: date = Field(default_factory=date.today)

@router.post("/create-post", response_model=PostResponse)
async def create_post(db:db_dependency,
                      post: PostCreate,
                      user: Annotated[dict, Depends(get_current_user)]
                      ):

    new_post = Post(
        title=post.title,
        body=post.body,
        slug=post.slug,
        date_posted=post.date_posted,
        author_id=user['id']
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.post(
    "/create-comment/{post_id}/comment",
    response_model=CommentsResponse)
async def create_comment(db:db_dependency,
                         post_id: int,
                         comment: CommentCreate,
                         user: Annotated[dict, Depends(get_current_user)]
                         ):
    posts = db.query(Post).filter(Post.id == post_id).first()
    if not posts:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        comment_body=comment.comment_body,
        post_id=post_id,
        author_id=user['id']
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/get_comments_by_user_id", response_model=List[CommentsResponse])
async def get_comments(db:db_dependency, user: Annotated[dict, Depends(get_current_user)]):
    comments = db.query(Comment).filter(Comment.author_id == user['id']).all()
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")
    return comments

@router.get("/post", response_model=List[PostResponse])
async def get_post_by_user_id(
    db: db_dependency,
    user: Annotated[dict, Depends(get_current_user)]
):
    posts = db.query(Post).filter(Post.author_id == user["id"]).all()

    if not posts:
        raise HTTPException(status_code=404, detail="No posts found")

    return posts


@router.put("/update-post/{post_id}", response_model=List[PostResponse])
async def update_post(db: db_dependency,
                      post: PostUpdate,
                      post_id: int,
                      user: Annotated[dict, Depends(get_current_user)]
                      ):
    post_model = db.query(Post).filter((Post.id == post_id) & (Post.author_id == user['id']) ).first()
    if not post_model:
        raise HTTPException(status_code=404, detail="Post not found")
    post_model.title = post.title
    post_model.body = post.body
    post_model.slug = post.slug
    post_model.date_posted = post.date_posted

    db.add(post_model)
    db.commit()
    return post_model