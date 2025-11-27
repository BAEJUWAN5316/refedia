from database import SessionLocal
from db_models import User
from auth import verify_employee_id

def check_user():
    db = SessionLocal()
    email = "bae@socialmc.co.kr"
    employee_id = "TH251110"
    
    print(f"🔍 Checking user: {email}")
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        print(f"✅ User found: {user.name} (ID: {user.id})")
        print(f"   Is Approved: {user.is_approved}")
        print(f"   Is Admin: {user.is_admin}")
        print(f"   Stored Hash: {user.employee_id_hash}")
        
        # Verify password
        is_valid = verify_employee_id(employee_id, user.employee_id_hash)
        print(f"🔐 Password check ({employee_id}): {'✅ Match' if is_valid else '❌ Mismatch'}")
    else:
        print("❌ User not found")
    
    db.close()

if __name__ == "__main__":
    check_user()
