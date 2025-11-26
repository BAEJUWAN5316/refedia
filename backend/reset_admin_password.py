from database import SessionLocal
from db_models import User
from auth import hash_employee_id

def reset_admin_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "bae@socialmc.co.ke").first()
        if user:
            print(f"Found admin user: {user.email}")
            user.employee_id_hash = hash_employee_id("1234")
            db.commit()
            print("✅ Password reset to '1234'")
        else:
            print("❌ Admin user not found")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
