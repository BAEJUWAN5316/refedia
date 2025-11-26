from database import engine, SessionLocal, Base
from db_models import User
from auth import hash_employee_id

def init_database():
    """데이터베이스 테이블 생성"""
    print("🔨 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")


def create_admin_user():
    """기본 관리자 계정 생성"""
    db = SessionLocal()
    
    try:
        # 기존 관리자 확인
        existing_admin = db.query(User).filter(User.email == "bae@socialmc.co.kr").first()
        
        if existing_admin:
            print("⚠️ Admin user already exists. Skipping...")
            return
        
        # 관리자 계정 생성
        admin_user = User(
            email="bae@socialmc.co.kr",
            name="배주완",
            employee_id_hash=hash_employee_id("TH251110"),
            is_approved=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("   Email: bae@socialmc.co.kr")
        print("   Employee ID: TH251110")
    
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Refedia Database Initialization")
    print("=" * 50)
    
    init_database()
    create_admin_user()
    
    print("\n" + "=" * 50)
    print("✅ Initialization complete!")
    print("=" * 50)
    print("\nYou can now start the server with:")
    print("  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
