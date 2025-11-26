import redis
import json
from typing import Optional, List
from db_config import REDIS_URL, FRAME_CACHE_EXPIRE_SECONDS

# Redis 클라이언트 초기화
redis_client = None

if REDIS_URL:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()  # 연결 테스트
        print(f"[OK] Redis connected: {REDIS_URL}")
    except Exception as e:
        print(f"[WARN] Redis connection failed: {e}. Caching disabled.")
        redis_client = None
else:
    print("[WARN] REDIS_URL not set. Caching disabled.")


def get_cached_frames(url: str, count: int = 4) -> Optional[List[str]]:
    """캐시에서 프레임 가져오기"""
    if not redis_client:
        return None
    
    try:
        cache_key = f"frames:{url}:{count}"
        cached = redis_client.get(cache_key)
        if cached:
            print(f"[OK] Cache HIT for {url}")
            return json.loads(cached)
        else:
            print(f"[WARN] Cache MISS for {url}")
            return None
    except Exception as e:
        print(f"[ERROR] Redis get error: {e}")
        return None


def set_cached_frames(url: str, frames: List[str], count: int = 4):
    """프레임을 캐시에 저장 (TTL: 5분)"""
    if not redis_client:
        return
    
    try:
        cache_key = f"frames:{url}:{count}"
        redis_client.setex(
            cache_key,
            FRAME_CACHE_EXPIRE_SECONDS,
            json.dumps(frames)
        )
        print(f"[OK] Cached frames for {url} (TTL: {FRAME_CACHE_EXPIRE_SECONDS}s)")
    except Exception as e:
        print(f"[ERROR] Redis set error: {e}")


def clear_frame_cache(url: str):
    """특정 URL의 캐시 삭제"""
    if not redis_client:
        return
    
    try:
        pattern = f"frames:{url}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            print(f"[OK] Cleared cache for {url}")
    except Exception as e:
        print(f"[ERROR] Redis delete error: {e}")
