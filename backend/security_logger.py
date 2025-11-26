import logging
from datetime import datetime
import os

# 로그 디렉토리 생성
os.makedirs("logs", exist_ok=True)

# 보안 이벤트 전용 로거
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# 파일 핸들러
handler = logging.FileHandler("logs/security.log", encoding="utf-8")
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
security_logger.addHandler(handler)

# 콘솔 핸들러 (개발 시 확인용)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
security_logger.addHandler(console_handler)


def log_login_attempt(email: str, success: bool, ip: str):
    """로그인 시도 로깅"""
    if success:
        security_logger.info(f"Login SUCCESS: {email} from {ip}")
    else:
        security_logger.warning(f"Login FAILED: {email} from {ip}")


def log_unauthorized_access(user_id: int, resource: str, ip: str):
    """권한 없는 접근 시도 로깅"""
    security_logger.warning(
        f"UNAUTHORIZED: User {user_id} attempted to access {resource} from {ip}"
    )


def log_security_event(event_type: str, details: str, ip: str = "unknown"):
    """일반 보안 이벤트 로깅"""
    security_logger.info(f"{event_type}: {details} from {ip}")
