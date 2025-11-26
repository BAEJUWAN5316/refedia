from database import SessionLocal
from db_models import Post, User
from youtube_service import extract_youtube_metadata

def test_db_insert():
    db = SessionLocal()
    try:
        # Get admin user
        user = db.query(User).filter(User.email == "bae@socialmc.co.ke").first()
        if not user:
            print("❌ Admin user not found")
            return
        
        print(f"✅ Found user: {user.name} (ID: {user.id})")
        
        # Extract metadata
        url = "https://www.youtube.com/watch?v=weDePxQfiMo"
        print(f"\n🔍 Extracting metadata for {url}...")
        title, thumbnail, video_type = extract_youtube_metadata(url)
        print(f"✅ Metadata: {title[:50]}..., {video_type}")
        
        # Create post
        print(f"\n📝 Creating post in database...")
        new_post = Post(
            url=url,
            title=title,
            thumbnail=thumbnail,
            platform="youtube",
            video_type=video_type,
            primary_categories=["1"],  # Dummy category ID
            secondary_categories=["2"],  # Dummy category ID
            memo="Test post",
            user_id=user.id
        )
        
        print("💾 Adding to session...")
        db.add(new_post)
        
        print("💾 Committing...")
        db.commit()
        
        print("✅ Refreshing...")
        db.refresh(new_post)
        
        print(f"\n✅ SUCCESS! Post created with ID: {new_post.id}")
        print(f"   Title: {new_post.title}")
        print(f"   URL: {new_post.url}")
        print(f"   Author: {new_post.user_id}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_db_insert()
