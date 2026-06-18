from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, Response, Body
from dotenv import load_dotenv
import os

load_dotenv()

from sqlalchemy import or_, String
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid
import base64
import os
from datetime import timedelta, datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import engine, get_db, Base
from db_models import User, Category, Post as DBPost
from models import (
    UserCreate, UserLogin, UserResponse, UserApprove, UserMakeAdmin, UserRevokeAdmin,
    PasswordVerify, Token,
    CategoryCreate, CategoryResponse,
    PostCreate, PostUpdate, PostResponse,
)
from auth import (
    hash_employee_id, verify_employee_id, create_access_token,
    get_current_user, get_current_approved_user, get_current_admin_user, get_current_user_optional,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from youtube_service import extract_youtube_metadata, extract_frames, validate_youtube_url
from security_logger import log_login_attempt, log_security_event

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

def check_and_migrate_db():
    """DB 스키마 마이그레이션 (컬럼 추가 등)"""
    from sqlalchemy import text, inspect
    
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('posts')]
    
    with engine.connect() as conn:
        # 1. view_count 컬럼 추가
        if 'view_count' not in columns:
            print("🔄 Migrating: Adding view_count column to posts table...")
            try:
                # SQLite & Postgres compatible
                conn.execute(text("ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0"))
                conn.commit() # 커밋 필요
                print("✅ Added view_count column")
            except Exception as e:
                print(f"⚠️ Failed to add view_count column: {e}")

        # 2. Rename author_id -> user_id
        if 'author_id' in columns and 'user_id' not in columns:
            print("🔄 Migrating: Renaming author_id to user_id...")
            try:
                conn.execute(text("ALTER TABLE posts RENAME COLUMN author_id TO user_id"))
                conn.commit()
                print("✅ Renamed author_id to user_id")
            except Exception as e:
                print(f"⚠️ Failed to rename author_id: {e}")

        # 3. Rename primary_category -> industry_categories
        if 'primary_category' in columns and 'industry_categories' not in columns:
            print("🔄 Migrating: Renaming primary_category to industry_categories...")
            try:
                conn.execute(text("ALTER TABLE posts RENAME COLUMN primary_category TO industry_categories"))
                conn.commit()
                print("✅ Renamed primary_category to industry_categories")
            except Exception as e:
                print(f"⚠️ Failed to rename primary_category: {e}")
        elif 'primary_categories' in columns and 'industry_categories' not in columns:
             print("🔄 Migrating: Renaming primary_categories to industry_categories...")
             try:
                conn.execute(text("ALTER TABLE posts RENAME COLUMN primary_categories TO industry_categories"))
                conn.commit()
                print("✅ Renamed primary_categories to industry_categories")
             except Exception as e:
                print(f"⚠️ Failed to rename primary_categories: {e}")

        # 4. Rename secondary_category -> genre_categories
        if 'secondary_category' in columns and 'genre_categories' not in columns:
            print("🔄 Migrating: Renaming secondary_category to genre_categories...")
            try:
                conn.execute(text("ALTER TABLE posts RENAME COLUMN secondary_category TO genre_categories"))
                conn.commit()
                print("✅ Renamed secondary_category to genre_categories")
            except Exception as e:
                print(f"⚠️ Failed to rename secondary_category: {e}")
        elif 'secondary_categories' in columns and 'genre_categories' not in columns:
             print("🔄 Migrating: Renaming secondary_categories to genre_categories...")
             try:
                conn.execute(text("ALTER TABLE posts RENAME COLUMN secondary_categories TO genre_categories"))
                conn.commit()
                print("✅ Renamed secondary_categories to genre_categories")
             except Exception as e:
                print(f"⚠️ Failed to rename secondary_categories: {e}")

        # 5. Add new columns: cast, mood, editing
        new_cols = ['cast_categories', 'mood_categories', 'editing_categories']
        for col_name in new_cols:
            if col_name not in columns:
                print(f"🔄 Migrating: Adding {col_name} column...")
                try:
                    # JSON type support varies, using Text or JSON depending on DB
                    # SQLAlchemy JSON type usually maps to JSON in Postgres and JSON/TEXT in SQLite
                    # Here we use generic ADD COLUMN. SQLite doesn't support JSON type in ALTER TABLE easily without extensions sometimes, 
                    # but SQLAlchemy handles it if we define it in model. 
                    # For raw SQL:
                    conn.execute(text(f"ALTER TABLE posts ADD COLUMN {col_name} JSON DEFAULT '[]'"))
                    conn.commit()
                    print(f"✅ Added {col_name} column")
                except Exception as e:
                    print(f"⚠️ Failed to add {col_name} (trying TEXT fallback): {e}")
                    try:
                        conn.execute(text(f"ALTER TABLE posts ADD COLUMN {col_name} TEXT DEFAULT '[]'"))
                        conn.commit()
                        print(f"✅ Added {col_name} column (TEXT)")
                    except Exception as e2:
                         print(f"⚠️ Failed to add {col_name}: {e2}")

        # 6. Add channel_name column
        if 'channel_name' not in columns:
            print("🔄 Migrating: Adding channel_name column...")
            try:
                conn.execute(text("ALTER TABLE posts ADD COLUMN channel_name VARCHAR"))
                conn.commit()
                print("✅ Added channel_name column")
            except Exception as e:
                print(f"⚠️ Failed to add channel_name column: {e}")

        # 6. Check Favorites table for 'id' column
        if 'favorites' in inspector.get_table_names():
            fav_columns = [col['name'] for col in inspector.get_columns('favorites')]
            if 'id' not in fav_columns:
                print("🔄 Migrating: Adding id column to favorites table...")
                try:
                    # Postgres specific (SERIAL)
                    # Try adding as PK first
                    try:
                        conn.execute(text("ALTER TABLE favorites ADD COLUMN id SERIAL PRIMARY KEY"))
                        conn.commit()
                        print("✅ Added id column to favorites (PK)")
                    except Exception as pk_err:
                        print(f"⚠️ Failed to add id as PK: {pk_err}")
                        conn.rollback()
                        # Fallback: Add as regular column
                        conn.execute(text("ALTER TABLE favorites ADD COLUMN id SERIAL"))
                        conn.commit()
                        print("✅ Added id column to favorites (Non-PK)")
                        
                except Exception as e:
                    print(f"⚠️ Failed to add id column to favorites (Postgres method): {e}")
                    try:
                        # Fallback for SQLite
                        conn.execute(text("ALTER TABLE favorites ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT"))
                        conn.commit()
                        print("✅ Added id column to favorites (SQLite method)")
                    except Exception as e2:
                        print(f"⚠️ Failed to add id column to favorites (SQLite method): {e2}")

        # 7. Migrate Category Types (Data Migration)
        # primary -> industry, secondary -> genre
        try:
            conn.execute(text("UPDATE categories SET type='industry' WHERE type='primary'"))
            conn.execute(text("UPDATE categories SET type='genre' WHERE type='secondary'"))
            conn.commit()
            print("✅ Migrated category types (primary->industry, secondary->genre)")
        except Exception as e:
            print(f"⚠️ Failed to migrate category types: {e}")

# 마이그레이션 실행
try:
    check_and_migrate_db()
except Exception as e:
    print(f"⚠️ DB Migration failed: {e}")

app = FastAPI(title="Refedia API", version="1.0.0")

# Rate Limiter 설정
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정 (환경 변수 사용)
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,https://www.cloudno7.co.kr,https://refedia-dev.up.railway.app,https://web-production-48b40b.up.railway.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"❌ Global Error: {error_msg}")
        with open("global_error.log", "a") as f:
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Path: {request.url.path}\n")
            f.write(f"Error: {str(e)}\n")
            f.write(f"Traceback:\n{error_msg}\n")
            f.write("-" * 50 + "\n")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e)}
        )

# HTTPS 강제 리다이렉트 (프로덕션만)
@app.middleware("http")
async def https_redirect_middleware(request: Request, call_next):
    if os.getenv("ENVIRONMENT") == "production":
        if request.headers.get("x-forwarded-proto") == "http":
            url = str(request.url).replace("http://", "https://", 1)
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url, status_code=301)
    return await call_next(request)

# ========================================
# Health Check
# ========================================

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Refedia API is running"}

    return {"status": "ok", "message": "Refedia API is running"}

# Debug System Endpoint (Moved to top for priority)
@app.get("/api/debug/system")
def debug_system():
    """시스템 상태 점검 (관리자 전용 - 현재는 공개)"""
    import subprocess
    import shutil
    
    result = {
        "ffmpeg": "Not found",
        "yt-dlp": "Not found",
        "python": "Unknown",
        "connectivity": "Unknown"
    }
    
    # 1. Check ffmpeg
    if shutil.which("ffmpeg"):
        try:
            out = subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT).decode()
            result["ffmpeg"] = out.split('\n')[0]
        except Exception as e:
            result["ffmpeg"] = f"Error: {str(e)}"
            
    # 2. Check yt-dlp
    try:
        out = subprocess.check_output(["yt-dlp", "--version"], stderr=subprocess.STDOUT).decode()
        result["yt-dlp"] = out.strip()
    except Exception as e:
        result["yt-dlp"] = f"Error: {str(e)}"

    # 3. Check Python
    import sys
    result["python"] = sys.version

    # 4. Check Connectivity (Simple curl)
    try:
        out = subprocess.check_output(["curl", "-I", "https://www.youtube.com"], stderr=subprocess.STDOUT).decode()
        result["connectivity"] = "OK" if "200" in out or "301" in out or "302" in out else f"Unexpected: {out[:100]}"
    except Exception as e:
        result["connectivity"] = f"Error: {str(e)}"

    return result

# ... (omitted for brevity, will use multi_replace or targeted replace if needed, but here I am replacing the middleware section and the end of file)

# Actually, I should do this in chunks to be safe.
# First, remove middleware.


# ========================================
# Authentication API
# ========================================

@app.post("/api/auth/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """회원가입"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    # 사번 중복 확인
    all_users = db.query(User).all()
    for user in all_users:
        if verify_employee_id(user_data.employee_id, user.employee_id_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee ID already registered")
    hashed_employee_id = hash_employee_id(user_data.employee_id)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        employee_id_hash=hashed_employee_id,
        is_approved=False,  # 관리자 승인 필요
        is_admin=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=Token)
@limiter.limit("5/minute")  # 무차별 로그인 시도 방지
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """로그인 (사번 사용)"""
    client_ip = request.client.host if request.client else "unknown"
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        log_login_attempt(credentials.email, False, client_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or employee ID")
    
    if not verify_employee_id(credentials.employee_id, user.employee_id_hash):
        log_login_attempt(credentials.email, False, client_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or employee ID")
    
    if not user.is_approved:
        log_login_attempt(credentials.email, False, client_ip)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not approved by admin")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
    log_login_attempt(credentials.email, True, client_ip)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.post("/api/auth/verify-password")
def verify_password(data: PasswordVerify, current_user: User = Depends(get_current_user)):
    """비밀번호(사번) 재확인"""
    if not verify_employee_id(data.employee_id, current_user.employee_id_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid employee ID")
    return {"status": "verified"}

@app.post("/api/auth/logout")
def logout(request: Request, current_user: User = Depends(get_current_user)):
    """로그아웃 (Session-based, 클라이언트에서 sessionStorage 삭제)"""
    client_ip = request.client.host if request.client else "unknown"
    log_security_event("LOGOUT", f"User {current_user.email}", client_ip)
    return {"status": "logged out", "message": "Please clear your session storage"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """현재 사용자 정보"""
    return current_user

@app.get("/api/admin/users", response_model=List[UserResponse])
def get_all_users(current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """모든 사용자 조회 (관리자 전용)"""
    return db.query(User).all()

@app.put("/api/admin/users/{user_id}/approve")
def approve_user(user_id: int, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """사용자 승인 (관리자 전용)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_approved = True
    db.commit()
    return {"status": "approved", "user_id": user.id}

@app.put("/api/admin/users/{user_id}/make-admin")
def make_admin(user_id: int, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """관리자 지정 (관리자 전용)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    user.is_approved = True
    db.commit()
    return {"status": "admin_granted", "user_id": user.id}

@app.put("/api/admin/users/{user_id}/revoke-admin")
def revoke_admin(user_id: int, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """관리자 권한 회수 (관리자 전용)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot revoke your own admin privileges")
    user.is_admin = False
    db.commit()
    return {"status": "admin_revoked", "user_id": user.id}

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """사용자 계정 삭제 (관리자 전용)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")
    db.delete(user)
    db.commit()
    return {"status": "deleted", "user_id": user_id}

# ========================================
# Category API
# ========================================



@app.post("/api/categories", response_model=CategoryResponse)
def create_category(category_data: CategoryCreate, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """카테고리 생성 (관리자 전용)"""
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
    category_id = str(uuid.uuid4())
    new_category = Category(id=category_id, name=category_data.name, type=category_data.type)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: str, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """카테고리 삭제 (관리자 전용)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"status": "deleted", "category_id": category_id}



# ========================================
# YouTube API
# ========================================

@app.get("/api/youtube/frames")
@limiter.limit("10/minute")  # YouTube API 과도한 호출 방지
def get_youtube_frames(
    request: Request,
    url: str = Query(...), 
    count: int = Query(4), 
    current_user: User = Depends(get_current_approved_user)
):
    """YouTube 랜덤 프레임 추출 (Base64)"""
    if not validate_youtube_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid YouTube URL"
        )
    frames = extract_frames(url, count)
    if not frames:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to extract frames"
        )
    return {"frames": frames, "count": len(frames)}



# ========================================
# Category API (Duplicate - keeping second definition)
# ========================================

# ========================================
# Category API
# ========================================

@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """카테고리 목록 (primary/secondary 그룹화)"""
    # DB에서 가져온 후 Python에서 정렬 (DB Collation 차이 방지)
    categories = db.query(Category).all()
    
    def sort_key(c):
        return c.name.lower()

    industry = sorted([{"id": c.id, "name": c.name} for c in categories if c.type == "industry"], key=lambda x: x['name'].lower())
    genre = sorted([{"id": c.id, "name": c.name} for c in categories if c.type == "genre"], key=lambda x: x['name'].lower())
    cast = sorted([{"id": c.id, "name": c.name} for c in categories if c.type == "cast"], key=lambda x: x['name'].lower())
    mood = sorted([{"id": c.id, "name": c.name} for c in categories if c.type == "mood"], key=lambda x: x['name'].lower())
    editing = sorted([{"id": c.id, "name": c.name} for c in categories if c.type == "editing"], key=lambda x: x['name'].lower())

    return {
        "industry": industry,
        "genre": genre,
        "cast": cast,
        "mood": mood,
        "editing": editing,
    }


@app.post("/api/categories", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """카테고리 생성 (관리자 전용)"""
    # 이름 중복 확인
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )
    
    # UUID 생성
    category_id = str(uuid.uuid4())
    
    new_category = Category(
        id=category_id,
        name=category_data.name,
        type=category_data.type
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category


@app.delete("/api/categories/{category_id}")
def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """카테고리 삭제 (관리자 전용)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    
    return {"status": "deleted", "category_id": category_id}


# ========================================
# Post API
# ========================================

@app.post("/api/posts", response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_approved_user),
    db: Session = Depends(get_db)
):
    """게시물 생성"""
    try:
        print("DEBUG: INSIDE CREATE_POST - START")
        # HttpUrl 객체를 문자열로 변환
        url_str = str(post_data.url)
        
        # URL 유효성 검사
        if not validate_youtube_url(url_str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid YouTube URL"
            )
        
        # URL 중복 확인
        existing = db.query(DBPost).filter(DBPost.url == url_str).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Post with this URL already exists"
            )
            
        # YouTube 메타데이터 추출
        try:
            from youtube_service import extract_youtube_metadata
            title, thumbnail, video_type, _, channel_name = extract_youtube_metadata(url_str)
            if not title:
                title = "Unknown Title"
            if not thumbnail:
                thumbnail = ""
            if not video_type:
                video_type = "long"
            if not channel_name:
                channel_name = "Unknown Channel"
        except Exception as e:
            print(f"⚠️ Metadata extraction failed: {e}")
            title = "Unknown Title"
            thumbnail = ""
            video_type = "long"
            channel_name = "Unknown Channel"
        
        # 게시물 생성
        new_post = DBPost(
            url=url_str,
            title=title,
            channel_name=channel_name,
            thumbnail=thumbnail,
            platform="youtube",
            video_type=video_type,
            industry_categories=post_data.industry_categories,
            genre_categories=post_data.genre_categories,
            cast_categories=post_data.cast_categories,
            mood_categories=post_data.mood_categories,
            editing_categories=post_data.editing_categories,
            memo=post_data.memo,
            user_id=current_user.id
        )
        
        # 초기 조회수 가져오기
        try:
            vid = None
            if 'v=' in url_str:
                vid = url_str.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url_str:
                vid = url_str.split('youtu.be/')[1].split('?')[0]
            elif 'shorts/' in url_str:
                vid = url_str.split('shorts/')[1].split('?')[0]
                
            if vid:
                from youtube_service import update_view_counts_batch
                view_counts = update_view_counts_batch([vid])
                if vid in view_counts:
                    new_post.view_count = view_counts[vid]
                    print(f"✅ Initial view count fetched: {new_post.view_count}")
        except Exception as e:
            print(f"⚠️ Failed to fetch initial view count: {e}")
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return new_post

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"❌ Create post failed: {error_msg}")
        with open("error_log.txt", "a") as f:
            f.write(f"Create Post Error time: {datetime.now()}\n")
            f.write(f"Error: {str(e)}\n")
            f.write(f"Traceback:\n{error_msg}\n")
            f.write("-" * 50 + "\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


@app.post("/api/ai/analyze")
def analyze_video_category(
    url: str = Body(..., embed=True),
    current_user: User = Depends(get_current_approved_user),
    db: Session = Depends(get_db)
):
    """
    AI를 사용하여 비디오 URL을 분석하고 적절한 카테고리를 추천합니다.
    (텍스트 + 시각 정보 활용)
    """
    # 1. YouTube 메타데이터 추출
    try:
        from youtube_service import extract_youtube_metadata, extract_frames, download_image_as_base64
        title, thumbnail_url, _, description, channel_name = extract_youtube_metadata(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch YouTube metadata: {str(e)}")
        
    # 1.5 시각 정보 추출 (썸네일 + 프레임)
    images_data = []
    try:
        print("🖼️ Extracting visual data for AI analysis...")
        # 썸네일 다운로드
        if thumbnail_url:
            thumb_b64 = download_image_as_base64(thumbnail_url)
            if thumb_b64:
                images_data.append(thumb_b64)
        
        # 프레임 추출 (3장 정도만 추출하여 속도 최적화)
        frames = extract_frames(url, count=3)
        if frames:
            images_data.extend(frames)
            
        print(f"✅ Visual data ready: {len(images_data)} images")
    except Exception as e:
        print(f"⚠️ Failed to extract visual data: {e}")
        # 시각 정보 실패해도 텍스트 분석은 계속 진행
        
    # 2. 전체 카테고리 목록 조회
    categories = db.query(Category).all()
    categories_structure = {
        "industry": [{"id": c.id, "name": c.name} for c in categories if c.type == "industry"],
        "genre": [{"id": c.id, "name": c.name} for c in categories if c.type == "genre"],
        "cast": [{"id": c.id, "name": c.name} for c in categories if c.type == "cast"],
        "mood": [{"id": c.id, "name": c.name} for c in categories if c.type == "mood"],
        "editing": [{"id": c.id, "name": c.name} for c in categories if c.type == "editing"],
    }
    print(f"DEBUG: Fetched {len(categories)} categories from DB.")
    print(f"DEBUG: Structure sizes -> Industry: {len(categories_structure['industry'])}, Genre: {len(categories_structure['genre'])}")
    
    # 3. Gemini AI 분석 요청
    try:
        from ai_service import analyze_video_with_gemini
        # channel_name 및 images_data 추가 전달
        recommended_categories = analyze_video_with_gemini(
            title, 
            description, 
            categories_structure, 
            channel_name, 
            images_data
        )
        return recommended_categories
    except Exception as e:
        # 429 Error (Too Many Requests) 처리
        if "429" in str(e):
            raise HTTPException(status_code=429, detail="AI service is currently busy. Please try again later.")
        print(f"AI Analysis Error: {e}")
        # 디버깅을 위해 에러 메시지 상세 출력
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@app.get("/api/posts", response_model=List[PostResponse])
def get_posts(
    page: int = 1,
    limit: int = 20,
    industry_category: List[str] = Query(None),
    genre_category: List[str] = Query(None),
    cast_category: List[str] = Query(None),
    mood_category: List[str] = Query(None),
    editing_category: List[str] = Query(None),
    filter_logic: str = "AND",
    video_type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    my_posts: bool = False,
    favorites_only: bool = False,
    seed: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """게시물 목록 조회 (서버 사이드 필터링 & 페이지네이션)"""
    query = db.query(DBPost)
    
    # 0. My Posts & Favorites Filter
    if my_posts:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required for my_posts")
        query = query.filter(DBPost.user_id == current_user.id)
        
    if favorites_only:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required for favorites_only")
        # Favorite 모델이 필요함. db_models.py에 있는지 확인 필요.
        # 일단 Favorite 테이블과 조인하여 필터링
        from db_models import Favorite
        query = query.join(Favorite).filter(Favorite.user_id == current_user.id)

    # 1. Video Type
    if video_type and video_type != 'all':
        query = query.filter(DBPost.video_type == video_type)
        
    # 2. Search (Title, Memo)
    if search:
        import unicodedata
        # Normalize search term to both NFC and NFD to cover all bases
        search_nfc = unicodedata.normalize('NFC', search)
        search_nfd = unicodedata.normalize('NFD', search)
        
        search_pattern_nfc = f"%{search_nfc}%"
        search_pattern_nfd = f"%{search_nfd}%"
        
        query = query.filter(
            or_(
                DBPost.title.ilike(search_pattern_nfc),
                DBPost.title.ilike(search_pattern_nfd),
                DBPost.memo.ilike(search_pattern_nfc),
                DBPost.memo.ilike(search_pattern_nfd),
                DBPost.channel_name.ilike(search_pattern_nfc), # 채널명 검색 추가
                DBPost.channel_name.ilike(search_pattern_nfd)
            )
        )
    
    # 3. Date Range Filter
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(DBPost.created_at >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(DBPost.created_at < end_dt)
        except ValueError:
            pass
    
    # 4. Category Filter (JSON List Filtering)
    # 4. Category Filter (JSON List Filtering)
    # Helper for category filtering
    def apply_cat_filter(q, col, values, logic):
        if not values: return q
        if logic == 'AND':
            for val in values:
                q = q.filter(col.cast(String).like(f'%"{val}"%'))
        else: # OR
            conditions = [col.cast(String).like(f'%"{val}"%') for val in values]
            q = q.filter(or_(*conditions))
        return q

    if industry_category:
        query = apply_cat_filter(query, DBPost.industry_categories, industry_category, filter_logic)
    if genre_category:
        query = apply_cat_filter(query, DBPost.genre_categories, genre_category, filter_logic)
    if cast_category:
        query = apply_cat_filter(query, DBPost.cast_categories, cast_category, filter_logic)
    if mood_category:
        query = apply_cat_filter(query, DBPost.mood_categories, mood_category, filter_logic)
    if editing_category:
        query = apply_cat_filter(query, DBPost.editing_categories, editing_category, filter_logic)
        
    # Pagination & Sorting
    # Mix (Random Shuffle)
    if seed is not None:
        import random
        # 시드 기반 랜덤 정렬을 위해 전체 데이터를 가져온 후 메모리에서 섞거나,
        # DB 레벨에서 랜덤 정렬을 해야 함.
        # SQLite: ORDER BY RANDOM() - 시드 지원 안함
        # Python 메모리 정렬 방식 사용 (데이터가 많지 않다고 가정)
        posts = query.options(joinedload(DBPost.author)).all()
        random.seed(seed)
        random.shuffle(posts)
        
        # 페이지네이션 적용
        start = (page - 1) * limit
        end = start + limit
        posts = posts[start:end]
    else:
        # 기본 정렬 (최신순)
        skip = (page - 1) * limit
        posts = query.options(joinedload(DBPost.author))\
                     .order_by(DBPost.created_at.desc())\
                     .offset(skip)\
                     .limit(limit)\
                     .all()
        print(f"DEBUG: Fetched {len(posts)} posts")
    
    # 작성자 이름 및 좋아요 여부 설정
    try:
        import json
        for post in posts:
            if post.author:
                post.author_name = post.author.name
            
            # JSON 파싱 보정 (DB에 문자열로 저장된 경우)
            # JSON 파싱 보정 (DB에 문자열로 저장된 경우)
            for attr in ['industry_categories', 'genre_categories', 'cast_categories', 'mood_categories', 'editing_categories']:
                val = getattr(post, attr)
                if isinstance(val, str):
                    try:
                        setattr(post, attr, json.loads(val))
                    except:
                        setattr(post, attr, [])
        print("DEBUG: Author names and categories processed")
            
        # 좋아요 여부 확인
        if current_user:
            print(f"DEBUG: Checking favorites for user {current_user.id}")
            from db_models import Favorite
            # 최적화: 한 번의 쿼리로 현재 페이지의 모든 포스트에 대한 좋아요 여부 가져오기
            post_ids = [p.id for p in posts]
            if post_ids:
                favorites = db.query(Favorite).filter(
                    Favorite.user_id == current_user.id,
                    Favorite.post_id.in_(post_ids)
                ).all()
                favorited_post_ids = {f.post_id for f in favorites}
                
                for post in posts:
                    post.is_favorited = post.id in favorited_post_ids
            else:
                print("DEBUG: No posts to check favorites for")
            print("DEBUG: Favorites checked")
        else:
            for post in posts:
                post.is_favorited = False
            print("DEBUG: Anonymous user, favorites skipped")
            
        return posts
    except Exception as e:
        import traceback
        print(f"❌ Error in get_posts processing: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int, 
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """게시물 상세 조회"""
    post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # JSON 파싱 보정
    import json
    for attr in ['industry_categories', 'genre_categories', 'cast_categories', 'mood_categories', 'editing_categories']:
        val = getattr(post, attr)
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    setattr(post, attr, [str(x) for x in parsed])
                else:
                    setattr(post, attr, [])
            except:
                setattr(post, attr, [])
        elif isinstance(val, list):
             # 이미 리스트인 경우에도 문자열로 변환 (혹시 모를 정수형 ID 방지)
             setattr(post, attr, [str(x) for x in val])

    # 작성자 이름 설정
    if post.author:
        post.author_name = post.author.name
        
    # 좋아요 여부 확인
    if current_user:
        from db_models import Favorite
        is_favorited = db.query(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.post_id == post.id
        ).first() is not None
        post.is_favorited = is_favorited
    else:
        post.is_favorited = False
        
    # YouTube 조회수 동기화 제거 (성능 이슈)
    # 관리자가 '새로고침' 버튼을 눌렀을 때만 업데이트됨
        
    return post


@app.post("/api/posts/{post_id}/favorite")
def toggle_favorite(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """게시물 좋아요 토글"""
    from db_models import Favorite
    
    post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.post_id == post_id
    ).first()
    
    if favorite:
        db.delete(favorite)
        is_favorited = False
    else:
        new_favorite = Favorite(user_id=current_user.id, post_id=post_id)
        db.add(new_favorite)
        is_favorited = True
        
    db.commit()
    
    return {"is_favorited": is_favorited}


@app.put("/api/posts/{post_id}")
def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_approved_user),
    db: Session = Depends(get_db)
):
    """게시물 수정"""
    post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 권한 확인: 관리자이거나 작성자 본인
    if not current_user.is_admin and post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    
    try:
        # 업데이트
        # 업데이트
        if post_data.title is not None:
            post.title = post_data.title
        if post_data.industry_categories is not None:
            post.industry_categories = post_data.industry_categories
        if post_data.genre_categories is not None:
            post.genre_categories = post_data.genre_categories
        if post_data.cast_categories is not None:
            post.cast_categories = post_data.cast_categories
        if post_data.mood_categories is not None:
            post.mood_categories = post_data.mood_categories
        if post_data.editing_categories is not None:
            post.editing_categories = post_data.editing_categories
        if post_data.memo is not None:
            post.memo = post_data.memo
        if post_data.video_type is not None:
            post.video_type = post_data.video_type
        
        db.commit()
        db.refresh(post)
        
        return post
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"❌ Update post failed: {error_msg}")
        with open("error_log.txt", "a") as f:
            f.write(f"Error time: {datetime.now()}\n")
            f.write(f"Error: {str(e)}\n")
            f.write(f"Traceback:\n{error_msg}\n")
            f.write("-" * 50 + "\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update post: {str(e)}"
        )


@app.delete("/api/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_approved_user),
    db: Session = Depends(get_db)
):
    """게시물 삭제"""
    post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 권한 확인: 관리자이거나 작성자 본인
    if not current_user.is_admin and post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    
    return {"status": "deleted", "post_id": post_id}

@app.post("/api/admin/update-views")
def update_all_views(
    current_user: User = Depends(get_current_approved_user),
    db: Session = Depends(get_db)
):
    """관리자용: 모든 게시물의 조회수 강제 업데이트"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        posts = db.query(DBPost).all()
        video_ids = []
        post_map = {}
        
        for post in posts:
            vid = None
            if 'v=' in post.url:
                vid = post.url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in post.url:
                vid = post.url.split('youtu.be/')[1].split('?')[0]
            elif 'shorts/' in post.url:
                vid = post.url.split('shorts/')[1].split('?')[0]
                
            if vid:
                video_ids.append(vid)
                post_map[vid] = post
        
        updated_count = 0
        if video_ids:
            from youtube_service import update_view_counts_batch
            # 50개씩 배치 처리는 youtube_service 내부에서 함
            view_counts = update_view_counts_batch(video_ids)
            
            for vid, count in view_counts.items():
                if vid in post_map:
                    post = post_map[vid]
                    if post.view_count != count:
                        post.view_count = count
                        updated_count += 1
            
            db.commit()
            
        return {"status": "success", "updated_count": updated_count, "total_posts": len(posts)}
        
    except Exception as e:
        print(f"❌ Admin view update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/debug-db")
def debug_db(
    current_user: User = Depends(get_current_approved_user),
    db: Session = Depends(get_db)
):
    """DB 스키마 진단 및 강제 마이그레이션"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    from sqlalchemy import text, inspect
    
    result = {
        "status": "started",
        "tables": [],
        "posts_columns": [],
        "migration_attempted": False,
        "migration_success": False,
        "error": None
    }
    
    try:
        inspector = inspect(engine)
        result["tables"] = inspector.get_table_names()
        
        if "posts" in result["tables"]:
            columns = [col['name'] for col in inspector.get_columns('posts')]
            result["posts_columns"] = columns
            
            if "view_count" not in columns:
                result["migration_attempted"] = True
                try:
                    with engine.connect() as conn:
                        conn.execute(text("ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0"))
                        conn.commit()
                    result["migration_success"] = True
                    # Refresh columns
                    result["posts_columns"] = [col['name'] for col in inspector.get_columns('posts')]
                except Exception as e:
                    result["error"] = str(e)
        
        # Check Favorites table
        if "favorites" in result["tables"]:
             columns = [col['name'] for col in inspector.get_columns('favorites')]
             result["favorites_columns"] = columns
             
             if 'id' not in columns:
                 result["favorites_migration_attempted"] = True
                 try:
                     with engine.connect() as conn:
                         # Try adding as PK first
                         try:
                            conn.execute(text("ALTER TABLE favorites ADD COLUMN id SERIAL PRIMARY KEY"))
                            conn.commit()
                            result["favorites_migration_success"] = True
                            print("✅ Added id column to favorites (PK)")
                         except Exception as pk_err:
                            print(f"⚠️ Failed to add id as PK: {pk_err}")
                            conn.rollback()
                            # Fallback: Add as regular column (if PK already exists)
                            conn.execute(text("ALTER TABLE favorites ADD COLUMN id SERIAL"))
                            conn.commit()
                            result["favorites_migration_success"] = True
                            print("✅ Added id column to favorites (Non-PK)")
                            
                     # Refresh columns
                     result["favorites_columns"] = [col['name'] for col in inspector.get_columns('favorites')]
                 except Exception as e:
                     result["favorites_migration_error"] = str(e)
             
             # Test Favorite Query
             try:
                 from db_models import Favorite
                 fav_count = db.query(Favorite).count()
                 result["favorite_count"] = fav_count
                 result["favorite_query_test"] = "success"
             except Exception as e:
                 db.rollback() # Rollback transaction on error
                 result["favorite_query_test"] = "failed"
                 result["favorite_error"] = str(e)
        else:
             result["favorites_missing"] = True
        
        # 5. Runtime ORM Test
        try:
            # Test User query
            user_count = db.query(User).count()
            result["user_count"] = user_count
            
            # Test Post query
            posts = db.query(DBPost).limit(50).all()
            result["posts_checked"] = len(posts)
            result["validation_errors"] = []
            
            from models import PostResponse
            
            for i, post in enumerate(posts):
                try:
                    # Manually trigger Pydantic validation
                    PostResponse.model_validate(post)
                except Exception as e:
                    result["validation_errors"].append({
                        "post_id": post.id,
                        "error": str(e),
                        "data_preview": {
                            "primary_categories": post.primary_categories,
                            "secondary_categories": post.secondary_categories,
                            "video_type": post.video_type,
                            "platform": post.platform
                        }
                    })
                    if len(result["validation_errors"]) >= 5: # Limit errors
                        break
            
            if not result["validation_errors"]:
                result["orm_test"] = "success"
            else:
                result["orm_test"] = "failed_validation"
                
            # 6. Test Favorites Query Logic (Simulate get_posts)
            try:
                from db_models import Favorite
                # Use first user found or dummy ID 1
                test_user_id = 1
                # Use post IDs from above
                test_post_ids = [p.id for p in posts]
                
                if test_post_ids:
                    favs = db.query(Favorite).filter(
                        Favorite.user_id == test_user_id,
                        Favorite.post_id.in_(test_post_ids)
                    ).all()
                    result["favorites_logic_test"] = "success"
                    result["favorites_found"] = len(favs)
                else:
                    result["favorites_logic_test"] = "skipped_no_posts"
            except Exception as e:
                db.rollback()
                result["favorites_logic_test"] = "failed"
                result["favorites_logic_error"] = str(e)
            
        except Exception as e:
            db.rollback() # Rollback transaction on error
            import traceback
            result["orm_test"] = "failed"
            result["orm_error"] = str(e)
            result["orm_traceback"] = traceback.format_exc()

        return result
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}


# Image Download Proxy
# ========================================

# 허용된 이미지 도메인 (SSRF 방지)
ALLOWED_IMAGE_DOMAINS = [
    "i.ytimg.com",
    "img.youtube.com",
    "i9.ytimg.com"
]

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

@app.get("/api/download/image")
async def download_image(url: str = Query(...)):
    """외부 이미지 프록시 다운로드 (CORS 우회 + SSRF 방지)"""
    import httpx
    
    # 도메인 검증
    if not any(domain in url for domain in ALLOWED_IMAGE_DOMAINS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid image source. Only YouTube images are allowed."
        )
    
    # 내부 IP 차단 (SSRF 방지)
    blocked_patterns = ["localhost", "127.0.0.1", "0.0.0.0", "192.168.", "10.", "172."]
    if any(blocked in url.lower() for blocked in blocked_patterns):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access to internal resources is forbidden"
        )
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # 크기 검증
            if len(response.content) > MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image too large (max 10MB)"
                )
            
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "image/jpeg")
            )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to download image: {str(e)}"
        )

# ========================================
# Game Web Routing
# ========================================

@app.get("/game1")
async def get_game1():
    """Serve the 3D maneuver simulator game HTML file directly at /game1."""
    game_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "game", "입체기동_시뮬레이터_v1.html")
    if os.path.exists(game_file):
        return FileResponse(game_file)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Game file '입체기동_시뮬레이터_v1.html' not found"
    )

# ========================================
# Static File Serving (SPA Support)
# ========================================

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# frontend/dist 디렉토리가 존재하면 정적 파일 서빙
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # favicon.ico 등 루트 레벨 파일 처리
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse(os.path.join(frontend_dist, "favicon.ico"))

    # SPA Fallback
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API 경로는 제외 (확실하게 처리)
        if full_path.startswith("api") or full_path.startswith("/api"):
            raise HTTPException(status_code=404, detail="Not Found")
            
        # 파일이 존재하면 서빙
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # 그 외에는 index.html 반환 (SPA 라우팅)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

# Scheduler for Daily View Count Update
import threading
import time
from datetime import datetime, timedelta

def run_daily_scheduler():
    """매일 아침 9시에 조회수 업데이트 실행"""
    print("⏰ Daily scheduler started")
    while True:
        now = datetime.now()
        # 다음 9시 계산
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
            
        wait_seconds = (next_run - now).total_seconds()
        print(f"⏳ Next view count update in {wait_seconds/3600:.1f} hours ({next_run})")
        
        time.sleep(wait_seconds)
        
        try:
            print("🔄 Running daily view count update...")
            # DB 세션 생성 및 업데이트 로직 실행
            # 주의: 여기서는 app context 외부이므로 새로운 세션을 만들어야 함
            from database import SessionLocal
            from youtube_service import update_view_counts_batch
            
            db = SessionLocal()
            try:
                posts = db.query(DBPost).all()
                video_ids = []
                post_map = {}
                
                for post in posts:
                    vid = None
                    if 'v=' in post.url:
                        vid = post.url.split('v=')[1].split('&')[0]
                    elif 'youtu.be/' in post.url:
                        vid = post.url.split('youtu.be/')[1].split('?')[0]
                    elif 'shorts/' in post.url:
                        vid = post.url.split('shorts/')[1].split('?')[0]
                        
                    if vid:
                        video_ids.append(vid)
                        post_map[vid] = post
                
                if video_ids:
                    view_counts = update_view_counts_batch(video_ids)
                    updated_count = 0
                    for vid, count in view_counts.items():
                        if vid in post_map:
                            post = post_map[vid]
                            if post.view_count != count:
                                post.view_count = count
                                updated_count += 1
                    
                    db.commit()
                    print(f"✅ Daily update completed: {updated_count} posts updated")
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Daily update failed: {e}")

@app.on_event("startup")
async def startup_event():
    # 백그라운드 스레드로 스케줄러 실행
    thread = threading.Thread(target=run_daily_scheduler, daemon=True)
    thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
