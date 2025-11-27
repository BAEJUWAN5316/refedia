from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import User
from auth import hash_employee_id
import os

# Use test.db as that's what app_main.py is using now (due to missing DATABASE_URL)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def restore_admin():
    db = SessionLocal()
    try:
        email = "bae@socialmc.co.kr"
        employee_id = "TH251110"
        name = "Admin User"

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User {email} already exists.")
            user.is_approved = True
            user.is_admin = True
            user.employee_id_hash = hash_employee_id(employee_id) # Update hash just in case
            print("Updated existing user to admin.")
        else:
            print(f"Creating user {email}...")
            new_user = User(
                email=email,
                name=name,
                employee_id_hash=hash_employee_id(employee_id),
                is_approved=True,
                is_admin=True
            )
            db.add(new_user)
            print("Created new admin user.")
        
        db.commit()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    restore_admin()
