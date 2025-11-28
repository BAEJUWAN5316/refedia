from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    employee_id_hash = Column(String)
    is_approved = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    posts = relationship("Post", back_populates="author")
    favorites = relationship("Post", secondary="favorites", back_populates="favorited_by")


class Favorite(Base):
    __tablename__ = "favorites"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True)  # UUID
    name = Column(String, unique=True, nullable=False, index=True)
    type = Column(String, nullable=False)  # 'primary' or 'secondary'
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String)
    thumbnail = Column(String)
    platform = Column(String)
    video_type = Column(String)
    description = Column(String) # Keeping for backward compatibility if needed, but memo is main
    memo = Column(String, nullable=True) # New field for memo
    
    # Categories (stored as JSON strings for simplicity in SQLite)
    primary_category = Column(String) 
    secondary_category = Column(String, nullable=True)
    
    # Meta
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    view_count = Column(Integer, default=0)

    # Relationships
    author = relationship("User", back_populates="posts")
    favorited_by = relationship("User", secondary="favorites", back_populates="favorites")

    @property
    def primary_categories(self):
        import json
        if self.primary_category:
            try:
                return json.loads(self.primary_category)
            except:
                return []
        return []

    @primary_categories.setter
    def primary_categories(self, value):
        import json
        self.primary_category = json.dumps(value)

    @property
    def secondary_categories(self):
        import json
        if self.secondary_category:
            try:
                return json.loads(self.secondary_category)
            except:
                return []
        return []

    @secondary_categories.setter
    def secondary_categories(self, value):
        import json
        self.secondary_category = json.dumps(value)

    @property
    def user_id(self):
        return self.author_id
