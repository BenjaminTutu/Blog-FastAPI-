import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from sqlalchemy import String, Column, Integer, Date, DateTime, Boolean, ForeignKey, Text, UniqueConstraint


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default="user")
    date_joined: Mapped[Date] = mapped_column(Date, default=datetime.date.today)

#   relationship to users-table
    posts: Mapped[list['Post']] = relationship(back_populates="author")
    comments: Mapped[list["Comment"]] = relationship(back_populates="comment_author")
    user: Mapped[list[Like]] = relationship(back_populates="user")

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    date_posted: Mapped[Date] = mapped_column(Date, default=datetime.date.today)

    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    author: Mapped['User'] = relationship(back_populates="posts")
    comments: Mapped[list[Comment]] = relationship(back_populates="posts")
    likes: Mapped[list[Like]] = relationship(back_populates="post")


class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'))
    author_id = Column(Integer, ForeignKey('users.id'))
    comment_body: Mapped[str] = mapped_column(Text, nullable=False)
    date_posted: Mapped[Date] = mapped_column(Date, default=datetime.date.today)

    posts: Mapped['Post'] = relationship(back_populates="comments")
    comment_author: Mapped['User'] = relationship(back_populates="comments")


class Like(Base):
    __tablename__ = 'likes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

#     setting unique constraints
    __table_args__ = (
    UniqueConstraint('post_id', 'user_id'),
    )

    post: Mapped['Post'] = relationship(back_populates="likes")
    user: Mapped['User'] = relationship(back_populates="likes")



