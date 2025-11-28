from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from typing import Optional, List
from datetime import datetime


# User Models
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    employee_id: str = Field(..., min_length=6, max_length=20)  # 사번 최소 6자
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not v.replace('-', '').isalnum():
            raise ValueError('Employee ID must contain only alphanumeric characters')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    employee_id: str


class UserResponse(UserBase):
    id: int
    is_approved: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserApprove(BaseModel):
    user_id: int


class UserMakeAdmin(BaseModel):
    user_id: int


class UserRevokeAdmin(BaseModel):
    user_id: int


class PasswordVerify(BaseModel):
    employee_id: str


# Category Models
class CategoryCreate(BaseModel):
    name: str
    type: str  # 'primary' or 'secondary'


class CategoryResponse(BaseModel):
    id: str
    name: str
    type: str
    created_at: datetime

    class Config:
        from_attributes = True


# Post Models
class PostCreate(BaseModel):
    url: HttpUrl  # URL 형식 자동 검증
    primary_categories: List[str] = Field(..., min_items=1, max_items=5)
    secondary_categories: List[str] = Field(..., min_items=1, max_items=5)
    memo: Optional[str] = Field(None, max_length=1000)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    primary_categories: Optional[List[str]] = Field(None, max_items=5)
    secondary_categories: Optional[List[str]] = Field(None, max_items=5)
    memo: Optional[str] = Field(None, max_length=1000)
    video_type: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    url: str
    title: str
    thumbnail: Optional[str] = None
    platform: str
    video_type: str
    primary_categories: List[str]
    secondary_categories: List[str]
    memo: Optional[str] = None
    user_id: int
    author_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_favorited: bool = False
    view_count: int = 0

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # SQLAlchemy 모델에서 author_name 추출
        if hasattr(obj, "author") and obj.author:
            obj.author_name = obj.author.name
        return super().model_validate(obj, *args, **kwargs)

    @validator("primary_categories", "secondary_categories", pre=True)
    def parse_json_categories(cls, v):
        import json
        if isinstance(v, str):
            try:
                return json.loads(v)
            except ValueError:
                return []
        return v or []


# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserResponse] = None


class TokenData(BaseModel):
    email: Optional[str] = None
