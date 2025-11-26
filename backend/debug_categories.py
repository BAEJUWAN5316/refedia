from database import SessionLocal
from db_models import Post
from sqlalchemy import or_, String
import json

def debug_categories():
    db = SessionLocal()
    try:
        # 1. Get most recent post
        post = db.query(Post).order_by(Post.created_at.desc()).first()
        if not post:
            print("No posts found.")
            return

        # print(f"Most recent post: {post.title}")
        print(f"Primary: {post.primary_categories}")
        print(f"Secondary: {post.secondary_categories}")

        if not post.primary_categories:
            print("No primary categories to test.")
            return

        # 2. Test filtering
        target_cat = post.primary_categories[0]
        print(f"Testing filter for Primary Category ID: {target_cat}")

        # Logic from main.py (Revised for SQLite compatibility)
        # Using cast(String) and LIKE because JSON_EACH or contains might be flaky in this SQLite version
        query = db.query(Post)
        
        # We search for the category ID inside the JSON string
        # JSON array format: ["id1", "id2"]
        # So we look for "id1" (with quotes) to avoid partial matches
        conditions = [Post.primary_categories.cast(String).like(f'%"{target_cat}"%')]
        results = query.filter(or_(*conditions)).all()
        
        print(f"Found {len(results)} posts with filter.")
        found_ids = [p.id for p in results]
        if post.id in found_ids:
            print("✅ Filter works! Post found.")
        else:
            print("❌ Filter FAILED! Post not found.")
            
            # Debugging: Try naive string contains if JSON fails (common in SQLite)
            print("Attempting string contains debug...")
            str_query = db.query(Post).filter(Post.primary_categories.cast(str).contains(target_cat)).all()
            print(f"String contains found {len(str_query)} posts.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_categories()
