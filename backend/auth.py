from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from db_models import User

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer 토큰
security = HTTPBearer(auto_error=False)


def hash_employee_id(employee_id: str) -> str:
    """사번을 bcrypt로 해싱"""
    # bcrypt는 72자 제한이 있으므로 안전하게 자른다
    return pwd_context.hash(employee_id[:72])


def verify_employee_id(plain_employee_id: str, hashed_employee_id: str) -> bool:
    """사번 확인"""
    # bcrypt 72자 제한 처리
    return pwd_context.verify(plain_employee_id[:72], hashed_employee_id)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """현재 로그인한 사용자 가져오기"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_approved_user(current_user: User = Depends(get_current_user)) -> User:
    """승인된 사용자만 허용"""
    if not current_user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not approved by admin"
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """관리자만 허용"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """로그인한 경우 사용자 반환, 아니면 None"""
    if not credentials:
        print("DEBUG: No credentials provided")
        return None
        
    try:
        token = credentials.credentials
        print(f"DEBUG: Token received: {token[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        print(f"DEBUG: Email from token: {email}")
        if email is None:
            return None
    except JWTError as e:
        print(f"DEBUG: JWT Error: {e}")
        return None
    except Exception as e:
        print(f"DEBUG: Unexpected Error in auth: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    user = db.query(User).filter(User.email == email).first()
    print(f"DEBUG: User found: {user}")
    return user
