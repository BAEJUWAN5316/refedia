# Refedia - Reference Media Archive

## 📋 프로젝트 개요

YouTube 콘텐츠를 아카이빙하고 레퍼런스로 활용하기 위한 웹 애플리케이션입니다.
사내 직원들이 트렌드와 레퍼런스를 효율적으로 관리하고 공유할 수 있습니다.

### 핵심 기능
- ✅ YouTube URL 저장 및 관리
- ✅ Primary/Secondary 카테고리 시스템
- ✅ 롱폼/숏폼 자동 분류
- ✅ 검색 및 필터링
- ✅ YouTube 영상 랜덤 프레임 추출 (4개)
- ✅ 썸네일 자동 저장
- ✅ 사번 기반 인증 시스템
- ✅ 관리자 대시보드

---

## 🛠 기술 스택

### 백엔드
- **FastAPI** - Python 웹 프레임워크
- **SQLAlchemy** - ORM
- **SQLite** - 데이터베이스
- **JWT** - 토큰 기반 인증
- **bcrypt** - 비밀번호 해싱
- **yt-dlp** - YouTube 메타데이터 추출
- **opencv-python** - 비디오 프레임 추출
- 포트: `http://localhost:8000`

### 프론트엔드
- **React 18** (Vite)
- **Vanilla CSS** (다크 테마)
- 포트: `http://localhost:5173`

---

## 📂 프로젝트 구조

```
레퍼런스 저장소/
├── backend/
│   ├── main.py                    # FastAPI 앱 및 API 엔드포인트
│   ├── models.py                  # Pydantic 모델
│   ├── db_models.py               # SQLAlchemy ORM 모델
│   ├── database.py                # 데이터베이스 관리
│   ├── db_config.py               # 데이터베이스 설정
│   ├── auth.py                    # JWT/bcrypt 인증
│   ├── youtube_service.py         # YouTube API 서비스
│   ├── init_db_and_admin.py       # DB 초기화 스크립트
│   ├── requirements.txt           # Python 패키지
│   ├── refedia.db                 # SQLite 데이터베이스
│   ├── .env.example               # 환경변수 예시
│   └── images/                    # 추출된 프레임 이미지
│
└── frontend/
    ├── src/
    │   ├── App.jsx                # 메인 앱
    │   ├── main.jsx               # React 진입점
    │   ├── index.css              # 글로벌 스타일
    │   ├── auth.css               # 인증 페이지 스타일
    │   └── components/
    │       ├── Login.jsx          # 로그인
    │       ├── Signup.jsx         # 회원가입
    │       ├── PasswordCheckModal.jsx  # 비밀번호 확인 모달
    │       ├── AdminDashboard.jsx # 관리자 대시보드
    │       ├── PostCard.jsx       # 게시물 카드
    │       ├── PostDetail.jsx     # 게시물 상세
    │       ├── PostCreate.jsx     # 게시물 생성
    │       ├── CategoryFilter.jsx # 카테고리 필터
    │       ├── CategorySelector.jsx # 카테고리 선택기
    │       └── SearchBar.jsx      # 검색바
    │
    └── package.json
```

---

## 🗄️ 데이터베이스 스키마

### Users 테이블
- `id` (Integer, PK)
- `email` (String, Unique) - 이메일
- `name` (String) - 이름
- `employee_id_hash` (String) - 해시된 사번
- `is_approved` (Boolean) - 승인 여부
- `is_admin` (Boolean) - 관리자 여부
- `created_at` (DateTime) - 생성일

### Categories 테이블
- `id` (String, PK) - UUID
- `name` (String, Unique) - 카테고리명
- `type` (String) - primary/secondary
- `created_at` (DateTime) - 생성일

### Posts 테이블
- `id` (Integer, PK)
- `url` (String, Unique) - YouTube URL
- `title` (String) - 영상 제목
- `thumbnail` (String) - 썸네일 URL
- `platform` (String) - 플랫폼 (youtube)
- `video_type` (String) - long/short
- `primary_categories` (JSON) - Primary 카테고리 목록
- `secondary_categories` (JSON) - Secondary 카테고리 목록
- `memo` (String) - 메모
- `created_at` (DateTime) - 생성일
- `updated_at` (DateTime) - 수정일

---

## 🔌 API 엔드포인트

### 인증 API
- `POST /api/auth/signup` - 회원가입
- `POST /api/auth/login` - 로그인 (사번 사용)
- `POST /api/auth/verify-password` - 비밀번호 확인
- `GET /api/auth/me` - 현재 사용자 정보
- `GET /api/auth/users` - 모든 사용자 조회 (관리자)
- `POST /api/auth/users/approve` - 사용자 승인 (관리자)
- `POST /api/auth/users/make-admin` - 관리자 지정 (관리자)

### 게시물 API
- `GET /api/posts` - 게시물 목록 (필터링 지원)
  - Query params: `primary_category`, `secondary_category`, `video_type`, `search`
- `GET /api/posts/{post_id}` - 특정 게시물 조회
- `POST /api/posts` - 게시물 생성
- `PUT /api/posts/{post_id}` - 게시물 수정
- `DELETE /api/posts/{post_id}` - 게시물 삭제

### 카테고리 API
- `GET /api/categories` - 카테고리 목록 (primary/secondary 그룹화)
- `POST /api/categories` - 카테고리 생성 (UUID 자동 생성)
- `DELETE /api/categories/{category_id}` - 카테고리 삭제

### YouTube API
- `GET /api/youtube/frames?url={url}&count=4` - 랜덤 프레임 추출

### 이미지 다운로드
- `GET /api/download/image?url={url}` - 외부 이미지 프록시 다운로드

### 헬스 체크
- `GET /` - API 상태 확인

---

## 🚀 시작 가이드

### 1. 환경 설정

#### 백엔드
```bash
cd backend
pip install -r requirements.txt
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

#### 백엔드
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 프론트엔드
```bash
cd frontend
npm run dev
```

### 4. 브라우저 접속
- 프론트엔드: http://localhost:5173
- 백엔드 API 문서: http://localhost:8000/docs

---

## 📖 사용법

### 1. 회원가입 및 로그인
1. 회원가입 페이지에서 이메일, 이름, 사번 입력
2. 관리자 승인 대기
3. 승인 후 사번으로 로그인

### 2. 관리자 대시보드 접근
1. 관리자로 로그인
2. 우측 상단 **Admin Dashboard** 버튼 클릭
3. 사번 재입력 (보안 확인)

### 3. 카테고리 관리 (관리자)
1. Admin Dashboard > **Categories** 섹션
2. Category Name 입력
3. Type 선택 (Primary/Secondary)
4. **Add Category** 클릭

### 4. 게시물 추가
1. **+ Add Reference** 버튼 클릭
2. YouTube URL 입력
   - 지원 형식: youtube.com/watch, youtu.be, youtube.com/shorts
3. Primary Category 선택 (필수)
4. Secondary Category 선택 (선택)
5. 메모 입력 (선택)
6. **Save Reference** 클릭

### 5. YouTube 프레임 추출
1. 저장된 게시물 클릭
2. 상세 모달에서 4개의 랜덤 프레임 확인
3. **Refresh Frames** 버튼으로 새 프레임 생성
4. **Download** 버튼으로 이미지 저장

### 6. 검색 및 필터링
- 상단 카테고리 버튼으로 필터링
- Long/Short 버튼으로 영상 타입 필터링
- 검색창에 키워드 입력

---

## ⚙️ 주요 기능 상세

### 인증 시스템
- **사번 기반 인증**: 사번을 bcrypt로 해싱하여 저장
- **JWT 토큰**: 로그인 후 액세스 토큰 발급
- **관리자 권한**: 사용자 승인, 카테고리 관리, 게시물 수정/삭제

### YouTube 통합
- **메타데이터 자동 추출**: yt-dlp로 제목, 썸네일 가져오기
- **Rate Limit 처리**: YouTube API 제한 시 기본 제목으로 저장
- **롱폼/숏폼 자동 분류**: URL에 `/shorts/` 포함 여부로 판단
- **랜덤 프레임 추출**: opencv로 4개 랜덤 프레임 추출 및 다운로드
- **화질 요구사항**: 썸네일 및 프레임 추출 시 **원본 화질 유지 필수**

### 카테고리 시스템
- **Primary Category**: 주요 분류 (예: 콘텐츠, 마케팅)
- **Secondary Category**: 세부 분류 (예: 비디오, SNS)
- **다중 선택 가능**: 하나의 게시물에 여러 카테고리 지정

---

## ⚠️ 알려진 이슈 및 해결 방법

### 1. YouTube Rate Limit
**문제**: YouTube 요청이 많을 경우 rate limit 발생
**해결**: 
- youtube_service.py에 sleep 옵션 추가
- Rate limit 시 fallback 처리 (기본 제목으로 저장)

### 2. 로그인 실패
**문제**: 관리자 계정으로 로그인 안 됨
**해결**:
```bash
cd backend
rm refedia.db
python init_db_and_admin.py
```

### 3. CORS 에러
**문제**: 프론트엔드에서 API 호출 시 CORS 에러
**해결**: main.py에 CORS 미들웨어 설정되어 있음 (allow_origins=["*"])

### 4. 포트 충돌
**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID {프로세스ID} /F
```

---

## 🔧 개발 참고 사항

### 환경 변수 (.env)
```
DATABASE_URL=sqlite:///./refedia.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 데이터베이스 마이그레이션
현재는 SQLAlchemy의 `create_all()`로 테이블 생성
향후 Alembic 사용 권장

### 코드 수정 시 주의사항
1. 백엔드: uvicorn --reload로 자동 재로드
2. 프론트엔드: Vite HMR로 자동 반영
3. 데이터베이스 스키마 변경 시 마이그레이션 필요

### 유용한 스크립트
- `init_db_and_admin.py` - DB 초기화 및 관리자 생성
- `check_db.py` - DB 내용 확인
- `migrate_data.py` - 데이터 마이그레이션

---

## 🐛 디버깅

### 백엔드 로그
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### 프론트엔드 로그
브라우저 개발자 도구 (F12) > Console

### 데이터베이스 확인
```bash
cd backend
python check_db.py
```

---

## � 향후 개선 사항

### 기능
- [ ] Instagram 지원
- [ ] 북마크/즐겨찾기 기능
- [ ] 팀별 권한 관리
- [ ] 태그 시스템
- [ ] 대량 업로드

### 기술
- [ ] PostgreSQL 전환
- [ ] Redis 캐싱
- [ ] Celery 비동기 작업
- [ ] Docker 컨테이너화
- [ ] 배포 자동화 (Railway/Vercel)

---

## 📄 라이선스

내부 사용 목적

---

## 👥 개발자

- 초기 개발: Antigravity AI
- 유지보수: Social MC Team

---

## 📞 지원

문제 발생 시:
1. 백엔드/프론트엔드 서버 재시작
2. 데이터베이스 재초기화
3. 브라우저 캐시 삭제
4. 이슈가 지속되면 개발팀에 문의

---

**마지막 업데이트**: 2025-11-21  
**버전**: 2.0.0  
**상태**: Production Ready (로그인 이슈 해결 필요)
