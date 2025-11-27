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
    print(f"🔍 Extracting metadata for: {url}")
    
    # 1. Try oEmbed API first (Most reliable & Fast, avoids IP blocking)
    try:
        import requests
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(oembed_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            title = data.get('title')
            thumbnail = data.get('thumbnail_url')
            video_type = 'short' if '/shorts/' in url else 'long'
            print(f"✅ oEmbed extraction successful: {title}")
            
            # Force maxresdefault if possible
            if video_id := (url.split('v=')[1].split('&')[0] if 'v=' in url else None):
                    thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            return title, thumbnail, video_type
    except Exception as oembed_error:
        print(f"⚠️ oEmbed failed: {oembed_error}")

    # 2. Try yt-dlp (Fallback)
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
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
        print(f"❌ YouTube metadata extraction failed with yt-dlp: {e}")
        print("⚠️ Attempting manual fallback extraction...")
        
        try:
            # 3. Manual extraction (Regex/Requests)
            video_id = None
            if 'v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            elif 'shorts/' in url:
                video_id = url.split('shorts/')[1].split('?')[0]
            
            if video_id:
                # Construct Thumbnail URL
                thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                
                # Extract Title via Requests
                import requests
                import re
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=5)
                
                title = "YouTube Video"
                if response.status_code == 200:
                    matches = re.findall(r'<title>(.*?)</title>', response.text)
                    if matches:
                        title = matches[0].replace(" - YouTube", "")
                
                video_type = 'short' if '/shorts/' in url else 'long'
                
                print(f"✅ Manual extraction successful: {title}")
                return title, thumbnail, video_type
                
        except Exception as fallback_error:
            print(f"❌ Fallback extraction also failed: {fallback_error}")

        # Final Fallback
        video_type = 'short' if '/shorts/' in url else 'long'
        return "YouTube Video", None, video_type


def extract_frames(url: str, count: int = 4) -> List[str]:
    """
    YouTube 영상에서 랜덤 프레임 추출 (Base64)
    """
    # ffmpeg 확인
    import shutil
    if not shutil.which("ffmpeg"):
        print("❌ ffmpeg not found! Cannot extract frames.")
        return []

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
            'format': 'best[ext=mp4]/best',
            'outtmpl': temp_video_path,
            'quiet': True,
            'no_warnings': True,
            'overwrites': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_check_certificate': True,
            'geo_bypass': True,
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
