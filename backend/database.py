import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 환경 변수 직접 가져오기 (db_config 의존성 제거)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. URL이 없는 경우 (방어 코드)
if not DATABASE_URL:
    print("⚠️ DATABASE_URL 환경 변수가 없습니다. SQLite로 대체합니다.")
    DATABASE_URL = "sqlite:///./test.db"

# 3. URL 공백 제거 및 형식 수정 (postgres:// -> postgresql://)
# SQLAlchemy 1.4+ 에서는 postgres:// 형식을 더 이상 지원하지 않습니다.
DATABASE_URL = DATABASE_URL.strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 4. 엔진 생성
print(f"✅ DB 연결 시도: {DATABASE_URL[:10]}...")  # 로그 확인용 (앞부분만 출력)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True, # 연결 끊김 방지
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
