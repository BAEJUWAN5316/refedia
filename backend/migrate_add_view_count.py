from database import SessionLocal, engine
from sqlalchemy import text
import sys

def add_view_count_column():
    """posts 테이블에 view_count 컬럼 추가"""
    db = SessionLocal()
    
    print(f"🔌 Connected to database: {engine.url}")
    
    try:
        # Check if column exists
        try:
            # PostgreSQL specific check
            check_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='posts' AND column_name='view_count'")
            result = db.execute(check_query).scalar()
            if result:
                print("✅ 'view_count' column already exists (PostgreSQL check).")
                return
        except Exception:
            # SQLite fallback or general error
            pass

        print("🔧 Adding view_count column to posts table...")
        try:
            # Try adding the column
            db.execute(text("ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0"))
            db.commit()
            print("✅ 'view_count' column added successfully!")
        except Exception as e:
            if "duplicate column" in str(e) or "already exists" in str(e):
                print("✅ 'view_count' column already exists.")
            else:
                raise e
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    add_view_count_column()
    print("\n✅ Migration complete!")
