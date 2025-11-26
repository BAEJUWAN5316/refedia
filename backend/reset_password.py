from database import SessionLocal
from db_models import User
from auth import hash_employee_id

def reset_password():
    db = SessionLocal()
    email = "bae@socialmc.co.ke"
    new_password = "TH251110"
    
    print(f"🔄 Resetting password for: {email}")
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        new_hash = hash_employee_id(new_password)
        user.employee_id_hash = new_hash
        db.commit()
        print(f"✅ Password reset successful for {user.name}")
    else:
        print("❌ User not found")
    
    db.close()

if __name__ == "__main__":
    reset_password()
