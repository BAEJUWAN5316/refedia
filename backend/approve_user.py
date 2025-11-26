from database import SessionLocal
from db_models import User

def approve_user(email):
    """특정 사용자 승인"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return
        
        user.is_approved = True
        user.is_admin = True  # 관리자로도 설정
        db.commit()
        
        print(f"✅ User '{email}' approved and set as admin!")
        print(f"   Name: {user.name}")
        print(f"   Approved: {user.is_approved}")
        print(f"   Admin: {user.is_admin}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    approve_user("bae@socialmc.co.ke")
