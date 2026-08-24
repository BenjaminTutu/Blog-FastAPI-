from fastapi import Depends, APIRouter, HTTPException, status, Path
from sqlalchemy.orm import Session


from database import SessionLocal
from typing import Annotated, List
from pydantic import BaseModel, Field, ConfigDict
from models import *
from auth import get_current_user
from blog import get_db
from blog import PostResponse, CommentsResponse


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

db_dependency = Annotated[SessionLocal, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True
    role: str = Field(default="user")

    posts: list[PostResponse]
    comments: list[CommentsResponse]


@router.get("/users", response_model=List[UserResponse])
async def get_all_users_and_posts(db:db_dependency, user: user_dependency):
    if user is None or user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    users = db.query(User).all()
    return users

@router.get("/posts", response_model=List[PostResponse])
async def get_all_posts(db:db_dependency, user: user_dependency):
    if user is None or user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    posts = db.query(Post).all()
    return posts

@router.delete("/users/{user_id}")
async def delete_user_by_id(db:db_dependency, user: user_dependency, user_id: int = Path(gt=0)):
    if user is None or user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user_to_delete)
    db.commit()
    return {'message': f'User {user_id} was deleted'}

@router.delete("/post/{post_id}")
async def delete_post_by_id(db:db_dependency, user: user_dependency, post_id: int = Path(gt=0)):
    if user is None or user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not authorized")
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()
    return {'message': f'Post {post_id} was deleted'}








