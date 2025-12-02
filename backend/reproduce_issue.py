
import os
import sys
from dotenv import load_dotenv

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from youtube_service import extract_youtube_metadata, extract_frames, download_image_as_base64
from ai_service import analyze_video_with_gemini

# Sample URL (a popular video likely to work)
TEST_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 

def test_analysis():
    # Force UTF-8 for stdout
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    print(f"Testing analysis for: {TEST_URL}")
    
    try:
        # 1. Metadata
        print("1️⃣ Extracting metadata...")
        title, thumbnail_url, _, description, channel_name = extract_youtube_metadata(TEST_URL)
        print(f"   Title: {title}")
        print(f"   Thumbnail: {thumbnail_url}")
        
        # 2. Visual Data
        print("2️⃣ Extracting visual data...")
        images_data = []
        if thumbnail_url:
            thumb_b64 = download_image_as_base64(thumbnail_url)
            if thumb_b64:
                images_data.append(thumb_b64)
                print("   ✅ Thumbnail downloaded")
        
        frames = extract_frames(TEST_URL, count=1) # Just 1 frame for speed
        if frames:
            images_data.extend(frames)
            print(f"   ✅ {len(frames)} frames extracted")
            
        # 3. AI Analysis
        print("3️⃣ Calling Gemini...")
        
        # Fetch real categories from DB
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from db_models import Category
        
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        categories = db.query(Category).all()
        print(f"   Fetched {len(categories)} categories from DB")
        
        categories_structure = {
            "industry": [{"id": c.id, "name": c.name} for c in categories if c.type == "industry"],
            "genre": [{"id": c.id, "name": c.name} for c in categories if c.type == "genre"],
            "cast": [{"id": c.id, "name": c.name} for c in categories if c.type == "cast"],
            "mood": [{"id": c.id, "name": c.name} for c in categories if c.type == "mood"],
            "editing": [{"id": c.id, "name": c.name} for c in categories if c.type == "editing"],
        }
        db.close()
        
        result = analyze_video_with_gemini(
            title, description, categories_structure, channel_name, images_data
        )
        print("✅ Analysis Result:", result)

    except Exception as e:
        print("\n❌ ERROR CAUGHT:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analysis()
