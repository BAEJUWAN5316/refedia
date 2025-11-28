from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, Response
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
from dotenv import load_dotenv

load_dotenv()

from database import engine, get_db, Base
from db_models import User, Category, Post as DBPost, Favorite
from models import (
    UserCreate, UserLogin, UserResponse, UserApprove, UserMakeAdmin, UserRevokeAdmin,
    PasswordVerify, Token,
    CategoryCreate, CategoryResponse,
    PostCreate, PostUpdate, PostResponse,
)
from auth import (
    hash_employee_id, verify_employee_id, create_access_token,
    get_current_user, get_current_approved_user, get_current_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from youtube_service import extract_youtube_metadata, extract_frames, validate_youtube_url
from security_logger import log_login_attempt, log_security_event

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)



app = FastAPI(title="Refedia API", version="1.0.0")

# Startup Event: Create Admin User if not exists
@app.on_event("startup")
def startup_event():
    from database import SessionLocal
    db = SessionLocal()
    try:
        email = "bae@socialmc.co.kr"
        employee_id = "TH251110"
        name = "배주완"
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Creating initial admin user: {email}")
            new_user = User(
                email=email,
                name=name,
                employee_id_hash=hash_employee_id(employee_id),
                is_approved=True,
                is_admin=True
            )
            db.add(new_user)
            db.commit()
            print("✅ Initial admin user created successfully.")
        else:
            print(f"ℹ️ Admin user {email} already exists. Skipping creation.")
            
            # Ensure admin privileges (optional, but good for safety)
            if not user.is_admin or not user.is_approved:
                user.is_admin = True
                user.is_approved = True
                db.commit()
                print(f"✅ Updated existing user {email} to admin.")
                
    except Exception as e:
        print(f"❌ Failed to create initial admin user: {e}")
    finally:
        db.close()

# Rate Limiter 설정
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정 (환경 변수 사용)
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,https://www.cloudno7.co.kr,https://refedia-dev.up.railway.app"
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

# Frame extraction endpoint removed as per user request



# ========================================
# Category API (Duplicate - keeping second definition)
# ========================================

# ========================================
# Category API
# ========================================

@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """카테고리 목록 (primary/secondary 그룹화)"""
    # 이름순 정렬하여 조회
    categories = db.query(Category).order_by(Category.name).all()
    
    primary = [{"id": c.id, "name": c.name} for c in categories if c.type == "primary"]
    secondary = [{"id": c.id, "name": c.name} for c in categories if c.type == "secondary"]
    
    return {"primary": primary, "secondary": secondary}


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
        title, thumbnail, video_type = extract_youtube_metadata(url_str)
        
        # Normalize title to NFC
        import unicodedata
        if title:
            title = unicodedata.normalize('NFC', title)
        
        # 게시물 생성
        import json
        new_post = DBPost(
            url=url_str,
            title=title,
            thumbnail=thumbnail,
            platform="youtube",
            video_type=video_type,
            primary_category=json.dumps(post_data.primary_categories),
            secondary_category=json.dumps(post_data.secondary_categories),
            memo=post_data.memo,
            author_id=current_user.id
        )
        
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


@app.post("/api/admin/update-views")
def update_all_view_counts(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """모든 게시물의 조회수 업데이트 (관리자 전용)"""
    from youtube_service import update_view_counts_batch
    
    # 1. 모든 게시물 조회
    posts = db.query(DBPost).all()
    if not posts:
        return {"message": "No posts to update", "updated_count": 0}
    
    # 2. URL에서 Video ID 추출
    video_map = {} # {video_id: [post_obj, ...]} (같은 영상이 여러 번 있을 수도 있음)
    
    for post in posts:
        vid = None
        if 'v=' in post.url:
            vid = post.url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in post.url:
            vid = post.url.split('youtu.be/')[1].split('?')[0]
        elif 'shorts/' in post.url:
            vid = post.url.split('shorts/')[1].split('?')[0]
            
        if vid:
            if vid not in video_map:
                video_map[vid] = []
            video_map[vid].append(post)
            
    # 3. YouTube API로 조회수 가져오기 (배치 처리)
    all_video_ids = list(video_map.keys())
    print(f"🔄 Updating view counts for {len(all_video_ids)} videos...")
    
    view_counts = update_view_counts_batch(all_video_ids)
    
    # 4. DB 업데이트
    updated_count = 0
    for vid, count in view_counts.items():
        if vid in video_map:
            for post in video_map[vid]:
                post.view_count = count
                updated_count += 1
                
    db.commit()
    print(f"✅ Updated view counts for {updated_count} posts")
    
    return {"message": "View counts updated successfully", "updated_count": updated_count}


@app.get("/api/posts", response_model=List[PostResponse])
def get_posts(
    page: int = 1,
    limit: int = 20,
    primary_category: List[str] = Query(None),
    secondary_category: List[str] = Query(None),
    filter_logic: str = "AND",
    video_type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    seed: Optional[int] = None,
    my_posts: bool = False,
    favorites_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """게시물 목록 조회 (서버 사이드 필터링 & 페이지네이션)"""
    query = db.query(DBPost)
    
    # 0. User Specific Filters
    if my_posts:
        query = query.filter(DBPost.author_id == current_user.id)
        
    if favorites_only:
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
        print(f"DEBUG: Search term='{search}', NFC='{search_nfc}', NFD='{search_nfd}'")
        
        search_pattern_nfc = f"%{search_nfc}%"
        search_pattern_nfd = f"%{search_nfd}%"
        
        # DBPost에는 description 컬럼이 없으므로 title과 memo만 검색
        query = query.filter(
            or_(
                DBPost.title.ilike(search_pattern_nfc),
                DBPost.title.ilike(search_pattern_nfd),
                DBPost.memo.ilike(search_pattern_nfc),
                DBPost.memo.ilike(search_pattern_nfd)
            )
        )
    
    # 3. Date Range Filter
    if start_date:
        # start_date format: YYYY-MM-DD
        # created_at is DateTime, so compare with start of day
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(DBPost.created_at >= start_dt)
        except ValueError:
            pass # Invalid date format, ignore

    if end_date:
        # end_date format: YYYY-MM-DD
        # To include the end date fully, compare < end_date + 1 day
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(DBPost.created_at < end_dt)
        except ValueError:
            pass # Invalid date format, ignore
    
    # 4. Category Filter (JSON List Filtering)
    # SQLite/Generic: Cast JSON to String and use LIKE '%"cat_id"%'
    # This assumes JSON is stored as ["id1", "id2"] with double quotes.
    
    if primary_category:
        if filter_logic == 'AND':
            for cat_id in primary_category:
                query = query.filter(DBPost.primary_category.like(f'%"{cat_id}"%'))
        else: # OR
            conditions = [DBPost.primary_category.like(f'%"{cat_id}"%') for cat_id in primary_category]
            query = query.filter(or_(*conditions))

    if secondary_category:
        if filter_logic == 'AND':
            for cat_id in secondary_category:
                query = query.filter(DBPost.secondary_category.like(f'%"{cat_id}"%'))
        else: # OR
            conditions = [DBPost.secondary_category.like(f'%"{cat_id}"%') for cat_id in secondary_category]
            query = query.filter(or_(*conditions))
        
    # Pagination
    skip = (page - 1) * limit
    
    if seed is not None:
        # Seed-based Random Shuffle (Deterministic for same seed)
        # 1. Fetch ALL matching IDs
        all_ids = [id[0] for id in query.with_entities(DBPost.id).order_by(DBPost.created_at.desc()).all()]
        
        # 2. Shuffle IDs with seed
        import random
        random.Random(seed).shuffle(all_ids)
        
        # 3. Slice IDs for current page
        paged_ids = all_ids[skip : skip + limit]
        
        # 4. Fetch posts for paged_ids
        if not paged_ids:
            posts = []
        else:
            # Fetch posts (order is not guaranteed by IN clause)
            unsorted_posts = query.options(joinedload(DBPost.author))\
                                  .filter(DBPost.id.in_(paged_ids))\
                                  .all()
            
            # 5. Sort posts to match paged_ids order
            posts_map = {post.id: post for post in unsorted_posts}
            posts = [posts_map[id] for id in paged_ids if id in posts_map]
            
    else:
        # Standard Pagination (Created At Desc)
        posts = query.options(joinedload(DBPost.author))\
                     .order_by(DBPost.created_at.desc())\
                     .offset(skip)\
                     .limit(limit)\
                     .all()
    
    # 작성자 이름 및 즐겨찾기 여부 설정
    # 현재 사용자의 즐겨찾기 목록 조회 (성능 최적화를 위해 한 번에 조회)
    user_favorites = set()
    if current_user:
        favs = db.query(Favorite.post_id).filter(Favorite.user_id == current_user.id).all()
        user_favorites = {f[0] for f in favs}

    for post in posts:
        if post.author:
            post.author_name = post.author.name
        # 즐겨찾기 여부 설정
        post.is_favorited = post.id in user_favorites
        
    return posts


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """게시물 상세 조회"""
    post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 작성자 이름 설정
    if post.author:
        post.author_name = post.author.name
        
    # 즐겨찾기 여부 설정
    fav = db.query(Favorite).filter(
        Favorite.user_id == current_user.id, 
        Favorite.post_id == post_id
    ).first()
    post.is_favorited = bool(fav)
        
    return post


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
        if post_data.title is not None:
            post.title = post_data.title
        if post_data.primary_categories is not None:
            post.primary_categories = post_data.primary_categories
        if post_data.secondary_categories is not None:
            post.secondary_categories = post_data.secondary_categories
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


# Image Download Proxy
# ========================================

# 허용된 이미지 도메인 (SSRF 방지)
ALLOWED_IMAGE_DOMAINS = [
    "i.ytimg.com",
    "img.youtube.com",
    "i9.ytimg.com",
    "yt3.ggpht.com"
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

@app.post("/api/posts/{post_id}/favorite")
def toggle_favorite(
    post_id: int,
    current_user: User = Depends(get_current_approved_user),
    db: Session = Depends(get_db)
):
    """게시물 즐겨찾기 토글"""
    post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.post_id == post_id
    ).first()
    
    if favorite:
        db.delete(favorite)
        db.commit()
        return {"status": "removed", "is_favorited": False}
    else:
        new_favorite = Favorite(user_id=current_user.id, post_id=post_id)
        db.add(new_favorite)
        db.commit()
        return {"status": "added", "is_favorited": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
