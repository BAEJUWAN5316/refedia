from youtube_service import extract_youtube_metadata
import time

url = "https://www.youtube.com/watch?v=crHHvBDi698"

print(f"Testing metadata extraction for {url}...")
start = time.time()
try:
    title, thumbnail, video_type = extract_youtube_metadata(url)
    print(f"✅ Success in {time.time() - start:.2f}s")
    print(f"Title: {title}")
    print(f"Thumbnail: {thumbnail}")
    print(f"Type: {video_type}")
except Exception as e:
    print(f"❌ Failed: {e}")
