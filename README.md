# Refedia - Reference Media Archive

YouTube 콘텐츠를 아카이빙하고 레퍼런스로 활용하기 위한 웹 애플리케이션입니다.

## 🚀 빠른 시작

### 1. 환경 설정

#### 백엔드
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env 파일에서 SECRET_KEY 변경하세요!
```

#### 프론트엔드
```bash
cd frontend
npm install
```

### 2. 데이터베이스 초기화

```bash
cd backend
python init_db_and_admin.py
```

**기본 관리자 계정:**
- Email: `bae@socialmc.co.ke`
- 사번(비밀번호): `TH251110`

### 3. 서버 실행

#### 백엔드 (터미널 1)
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 프론트엔드 (터미널 2)
```bash
cd frontend
npm run dev
```

### 4. 접속

- 프론트엔드: http://localhost:5173
- 백엔드 API 문서: http://localhost:8000/docs

## 🛠 기술 스택

### 백엔드
- FastAPI - Python 웹 프레임워크
- SQLAlchemy - ORM (SQLite/PostgreSQL 지원)
- JWT - 토큰 기반 인증
- yt-dlp - YouTube 메타데이터 추출
- opencv-python - 비디오 프레임 추출
- Redis - 프레임 캐싱 (옵션)

### 프론트엔드
- React 18 + Vite
- Vanilla CSS (다크 테마)

## ✨ 주요 기능

- ✅ YouTube URL 저장 및 관리
- ✅ Primary/Secondary 카테고리 시스템
- ✅ 롱폼/숏폼 자동 분류
- ✅ 검색 및 필터링
- ✅ YouTube 영상 랜덤 프레임 추출 (4개)
- ✅ **Redis 캐싱** - 프레임을 5분간 캐싱
- ✅ **Base64 이미지** - 디스크 저장 없이 즉시 다운로드
- ✅ 사번 기반 인증 시스템
- ✅ 관리자 대시보드

## 🚢 Railway 배포

### 1. GitHub 레포지토리 생성

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/refedia.git
git push -u origin main
```

### 2. Railway 프로젝트 설정

1. [Railway](https://railway.app) 접속
2. "New Project" → "Deploy from GitHub"
3. 레포지토리 선택: `refedia`
4. **PostgreSQL 추가**: "Add Plugin" → PostgreSQL
5. **Redis 추가**: "Add Plugin" → Redis

### 3. 환경변수 설정 (Railway 대시보드)

```
SECRET_KEY=<강력한-랜덤-키-생성>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRAME_CACHE_EXPIRE_SECONDS=300
```

> Railway가 자동으로 `DATABASE_URL`, `REDIS_URL`을 설정합니다.

### 4. 데이터베이스 초기화

Railway 콘솔에서:
```bash
cd backend && python init_db_and_admin.py
```

### 5. 배포 완료!

Railway가 제공하는 URL로 접속하세요.

## 📖 사용법

### 1. 회원가입 및 로그인
- 회원가입 후 관리자 승인 대기
- 승인 후 사번으로 로그인

### 2. 관리자 대시보드 (관리자만)
- 사용자 승인 및 관리자 권한 부여
- 카테고리 추가/삭제

### 3. 게시물 추가
- "Add Reference" 클릭
- YouTube URL 입력
- Primary 카테고리 선택 (필수)
- Secondary 카테고리 선택 (선택)
- 메모 입력 (선택)

### 4. YouTube 프레임 추출
- 게시물 클릭
- "Refresh Frames" 버튼 클릭
- 4개의 랜덤 프레임 표시
- **첫 요청**: 프레임 추출 (느림)
- **두 번째 요청 (5분 이내)**: Redis 캐시에서 즉시 로드 (빠름)
- 이미지 다운로드 버튼 클릭으로 저장

### 5. 검색 및 필터링
- 상단 검색창: 제목 검색
- Primary/Secondary 카테고리 필터
- Long/Short 비디오 타입 필터

## 🔧 개발 참고

### 환경변수 (.env)

```
DATABASE_URL=sqlite:///./refedia.db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRAME_CACHE_EXPIRE_SECONDS=300
```

### API 엔드포인트

자세한 API 문서는 http://localhost:8000/docs 참조

#### 인증 API
- `POST /api/auth/signup` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/me` - 현재 사용자
- `GET /api/auth/users` - 모든 사용자 (관리자)
- `POST /api/auth/users/approve` - 사용자 승인 (관리자)

#### 카테고리 API
- `GET /api/categories` - 카테고리 목록
- `POST /api/categories` - 카테고리 생성 (관리자)
- `DELETE /api/categories/{id}` - 카테고리 삭제 (관리자)

#### 게시물 API
- `GET /api/posts` - 게시물 목록 (필터링 지원)
- `POST /api/posts` - 게시물 생성
- `PUT /api/posts/{id}` - 게시물 수정 (관리자)
- `DELETE /api/posts/{id}` - 게시물 삭제 (관리자)

#### YouTube API
- `GET /api/youtube/frames?url={url}&count=4` - 랜덤 프레임 추출

## 🎨 기술 하이라이트

### Redis 캐싱
- YouTube 프레임을 Base64로 인코딩하여 Redis에 5분간 캐싱
- 반복 요청 시 즉시 로드
- Redis 없어도 정상 동작 (graceful fallback)

### PostgreSQL/SQLite 자동 전환
- 로컬: SQLite
- 프로덕션: PostgreSQL
- 환경변수 `DATABASE_URL`로 자동 감지

### 원본 화질 프레임 추출
- opencv-python으로 고화질 PNG 추출
- 디스크 저장 없이 Base64로 즉시 전송
- YouTube 다운로드 후 자동 삭제

## 📄 라이선스

내부 사용 목적

---

**마지막 업데이트**: 2025-11-24  
**버전**: 1.0.0  
**상태**: Production Ready ✅
