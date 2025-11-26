from database import SessionLocal, engine
from sqlalchemy import text

def add_user_id_column():
    """posts 테이블에 user_id 컬럼 추가"""
    db = SessionLocal()
    
    try:
        # user_id 컬럼 추가
        print("🔧 Adding user_id column to posts table...")
        db.execute(text("ALTER TABLE posts ADD COLUMN user_id INTEGER REFERENCES users(id)"))
        db.commit()
        print("✅ user_id column added successfully!")
        
        # 기존 게시물에 기본 user_id 설정 (admin 사용자로)
        print("🔧 Setting default user_id for existing posts...")
        admin_user_query = text("SELECT id FROM users WHERE is_admin = 1 LIMIT 1")
        admin_id = db.execute(admin_user_query).scalar()
        
        if admin_id:
            update_query = text("UPDATE posts SET user_id = :user_id WHERE user_id IS NULL")
            db.execute(update_query, {"user_id": admin_id})
            db.commit()
            print(f"✅ Set user_id={admin_id} for existing posts")
        else:
            print("⚠️ No admin user found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    add_user_id_column()
    print("\n✅ Migration complete!")
