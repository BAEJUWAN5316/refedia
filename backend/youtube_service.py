import yt_dlp
import cv2
import numpy as np
import base64
import random
import tempfile
import os
from typing import Optional, Tuple, List
from redis_cache import get_cached_frames, set_cached_frames


def extract_youtube_metadata(url: str) -> Tuple[Optional[str], Optional[str], str, Optional[str]]:
    """
    YouTube URL에서 메타데이터 추출
    Returns: (title, thumbnail_url, video_type, description)
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
            # oEmbed doesn't provide description, so we might need fallback or just use title
            description = "" 
            video_type = 'short' if '/shorts/' in url else 'long'
            print(f"✅ oEmbed extraction successful: {title}")
            
            # Force maxresdefault if possible
            if video_id := (url.split('v=')[1].split('&')[0] if 'v=' in url else None):
                    thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            # oEmbed 성공하더라도 설명이 없으므로 yt-dlp 시도해볼 가치는 있음.
            # 하지만 속도를 위해 일단 oEmbed 성공 시 설명은 비워두거나, 
            # 필요하다면 yt-dlp를 '설명 추출용'으로만 돌릴 수도 있음.
            # 여기서는 일단 oEmbed가 빠르니 이걸 쓰고, 설명이 꼭 필요하면 아래 yt-dlp로 넘어가는 로직을 추가할 수 있음.
            # 사용자 요청은 "AI가 분석"이므로 설명이 있으면 좋음.
            # oEmbed는 설명을 안 주므로, AI 분석을 위해서는 yt-dlp를 우선 시도하는 게 나을 수도 있음.
            # 그러나 yt-dlp는 느림.
            # 절충안: oEmbed 실패 시에만 yt-dlp 사용하거나, 
            # AI 분석 요청 시에는 별도로 yt-dlp를 호출하는 함수를 만드는 게 나을 수도.
            # 일단 기존 로직 유지하되, description 추가.
            
            return title, thumbnail, video_type, description
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
            description = info.get('description', '')
            
            # 롱폼/숏폼 자동 분류
            if '/shorts/' in url:
                video_type = 'short'
            else:
                video_type = 'long'
            
            return title, thumbnail, video_type, description
    
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
                description = ""
                if response.status_code == 200:
                    matches = re.findall(r'<title>(.*?)</title>', response.text)
                    if matches:
                        title = matches[0].replace(" - YouTube", "")
                    
                    # Try to extract description from meta tag
                    desc_matches = re.findall(r'<meta name="description" content="(.*?)">', response.text)
                    if desc_matches:
                        description = desc_matches[0]
                
                video_type = 'short' if '/shorts/' in url else 'long'
                
                print(f"✅ Manual extraction successful: {title}")
                return title, thumbnail, video_type, description
                
        except Exception as fallback_error:
            print(f"❌ Fallback extraction also failed: {fallback_error}")

        # Final Fallback
        video_type = 'short' if '/shorts/' in url else 'long'
        return "YouTube Video", None, video_type, ""


def extract_frames(url: str, count: int = 4) -> List[str]:
    """
    YouTube 영상에서 랜덤 프레임 추출 (Base64)
    """
    # ffmpeg 확인 (imageio-ffmpeg 사용)
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"🎥 ffmpeg path: {ffmpeg_path}")
    
    if not ffmpeg_path or not os.path.exists(ffmpeg_path):
        print("❌ ffmpeg not found via imageio-ffmpeg!")
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
            'ignoreerrors': True, # Keep this to handle errors manually via file size check
            'no_check_certificate': True,
            'geo_bypass': True,
            'ffmpeg_location': ffmpeg_path,
            # 봇 탐지 회피를 위한 안드로이드 클라이언트 에뮬레이션
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            }
        }
        
        print(f"🎬 Downloading video from {url} to {temp_video_path}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 파일 확인
        if not os.path.exists(temp_video_path) or os.path.getsize(temp_video_path) == 0:
            raise Exception("Video download failed (empty file)")

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
        print(f"❌ Frame extraction failed: {e}")
        print("⚠️ Attempting fallback to Thumbnail as Frame...")
        
        # Fallback: Use Thumbnail as a "Frame"
        try:
            # Extract ID
            video_id = None
            if 'v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            elif 'shorts/' in url:
                video_id = url.split('shorts/')[1].split('?')[0]
                
            if video_id:
                thumb_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                import requests
                resp = requests.get(thumb_url, timeout=5)
                if resp.status_code == 200:
                    b64_thumb = base64.b64encode(resp.content).decode('utf-8')
                    # Return the thumbnail repeated 'count' times or just once? 
                    # Returning once is safer, frontend should handle it.
                    # But to satisfy "count", let's return it once.
                    fallback_frames = [f"data:image/jpeg;base64,{b64_thumb}"]
                    print("✅ Fallback successful: Returned thumbnail as frame")
                    return fallback_frames
        except Exception as fb_e:
            print(f"❌ Fallback failed: {fb_e}")
            
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


def update_view_counts_batch(video_ids: List[str]) -> dict:
    """
    YouTube Data API를 사용하여 여러 영상의 조회수를 한 번에 업데이트
    Args:
        video_ids: YouTube Video ID 리스트 (최대 50개)
    Returns:
        dict: {video_id: view_count}
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("⚠️ YOUTUBE_API_KEY not found in environment variables")
        return {}

    if not video_ids:
        return {}

    # 50개씩 청크로 나누어 처리 (API 제한)
    results = {}
    
    # Extract IDs from URLs if full URLs are passed (safety check)
    clean_ids = []
    for vid in video_ids:
        if 'v=' in vid:
            clean_ids.append(vid.split('v=')[1].split('&')[0])
        elif 'youtu.be/' in vid:
            clean_ids.append(vid.split('youtu.be/')[1].split('?')[0])
        elif 'shorts/' in vid:
            clean_ids.append(vid.split('shorts/')[1].split('?')[0])
        else:
            clean_ids.append(vid)

    import requests
    
    # Chunk size 50
    for i in range(0, len(clean_ids), 50):
        chunk = clean_ids[i:i+50]
        ids_str = ",".join(chunk)
        
        url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={ids_str}&key={api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    vid = item['id']
                    stats = item['statistics']
                    view_count = int(stats.get('viewCount', 0))
                    results[vid] = view_count
            else:
                print(f"❌ YouTube API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Failed to fetch view counts: {e}")
            
    return results
