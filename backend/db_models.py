from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    employee_id_hash = Column(String, nullable=False)  # 해시된 사번
    is_approved = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="author")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True)  # UUID
    name = Column(String, unique=True, nullable=False, index=True)
    type = Column(String, nullable=False)  # 'primary' or 'secondary'
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String)  # 썸네일 URL
    platform = Column(String, default="youtube")
    video_type = Column(String, nullable=False)  # 'long' or 'short'
    primary_categories = Column(JSON, default=list)  # Primary 카테고리 목록
    secondary_categories = Column(JSON, default=list)  # Secondary 카테고리 목록
    memo = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="posts")
    view_count = Column(Integer, default=0)


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorites")
    post = relationship("Post", back_populates="favorites")

User.favorites = relationship("Favorite", back_populates="user")
Post.favorites = relationship("Favorite", back_populates="post")
