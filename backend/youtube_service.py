import yt_dlp
import cv2
import numpy as np
import base64
import random
import tempfile
import os
from typing import Optional, Tuple, List
from redis_cache import get_cached_frames, set_cached_frames


def extract_youtube_metadata(url: str) -> Tuple[Optional[str], Optional[str], str]:
    """
    YouTube URL에서 메타데이터 추출
    Returns: (title, thumbnail_url, video_type)
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail')
            
            # 롱폼/숏폼 자동 분류
            if '/shorts/' in url:
                video_type = 'short'
            else:
                video_type = 'long'
            
            return title, thumbnail, video_type
    
    except Exception as e:
        print(f"❌ YouTube metadata extraction failed: {e}")
        # Fallback: URL에서 타입만 추출
        video_type = 'short' if '/shorts/' in url else 'long'
        return "YouTube Video", None, video_type


def extract_frames(url: str, count: int = 4) -> List[str]:
    """
    YouTube 영상에서 랜덤 프레임 추출 (Base64)
    
    Args:
        url: YouTube URL
        count: 추출할 프레임 개수
    
    Returns:
        Base64 인코딩된 이미지 리스트
    """
    # 캐시 확인
    cached = get_cached_frames(url, count)
    if cached:
        return cached
    
    frames_base64 = []
    temp_video_path = None
    
    try:
        # 임시 파일 경로
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            temp_video_path = tmp_file.name
        
        # YouTube 영상 다운로드 (최고 화질)
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Force mp4 for better compatibility
            'outtmpl': temp_video_path,
            'quiet': True,
            'no_warnings': True,
            'overwrites': True,
        }
        
        print(f"🎬 Downloading video from {url} to {temp_video_path}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 파일 확인
        if not os.path.exists(temp_video_path):
            raise Exception(f"Video file not found at {temp_video_path}")
            
        file_size = os.path.getsize(temp_video_path)
        print(f"📁 File size: {file_size} bytes")
        
        if file_size == 0:
            raise Exception("Downloaded file is empty")

        # OpenCV로 비디오 열기
        cap = cv2.VideoCapture(temp_video_path)
        if not cap.isOpened():
            raise Exception(f"Failed to open video file with OpenCV: {temp_video_path}")
        
        # 총 프레임 수
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            raise Exception("Video has no frames")
        
        print(f"📊 Total frames: {total_frames}")
        
        # 랜덤 프레임 위치 선택 (중복 방지)
        frame_positions = sorted(random.sample(range(total_frames), min(count, total_frames)))
        
        for pos in frame_positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = cap.read()
            
            if ret:
                # 프레임을 PNG로 인코딩 (고화질 유지)
                _, buffer = cv2.imencode('.png', frame)
                
                # Base64 인코딩
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                frames_base64.append(f"data:image/png;base64,{frame_base64}")
                
                print(f"✅ Extracted frame at position {pos}")
        
        cap.release()
        
        # 캐시에 저장
        if frames_base64:
            set_cached_frames(url, frames_base64, count)
        
        return frames_base64
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Frame extraction failed: {e}")
        print(f"   Detailed error: {error_details}")
        
        # Return empty list but log the error
        # In a real app, we might want to raise a specific exception that main.py can catch
        # For now, we return empty list and let main.py handle it (it raises 500 if empty)
        return []
    
    finally:
        # 임시 파일 삭제
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
                print(f"🗑️ Cleaned up temp file: {temp_video_path}")
            except Exception as e:
                print(f"⚠️ Failed to delete temp file: {e}")


def validate_youtube_url(url: str) -> bool:
    """YouTube URL 유효성 검사"""
    valid_patterns = [
        'youtube.com/watch',
        'youtu.be/',
        'youtube.com/shorts/'
    ]
    return any(pattern in url for pattern in valid_patterns)
