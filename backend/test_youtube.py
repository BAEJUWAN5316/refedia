from youtube_service import extract_youtube_metadata
import time

url = "https://www.youtube.com/watch?v=weDePxQfiMo"

print(f"Testing metadata extraction for {url}...")
start = time.time()
try:
    title, thumbnail, video_type = extract_youtube_metadata(url)
    elapsed = time.time() - start
    print(f"✅ Success in {elapsed:.2f}s")
    print(f"Title: {title}")
    print(f"Thumbnail: {thumbnail}")
    print(f"Type: {video_type}")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Failed in {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()
