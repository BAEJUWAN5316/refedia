import requests
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import User, Base

# Setup DB connection to approve user
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

API_URL = "http://localhost:8000/api"

def verify():
    # 1. Signup
    print("1. Signing up...")
    signup_data = {
        "email": "verify@test.com",
        "name": "Verify User",
        "employee_id": "VERIFY01"
    }
    try:
        res = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        if res.status_code == 200:
            print("   Signup successful")
        elif res.status_code == 400 and "already registered" in res.text:
            print("   User already exists, proceeding...")
        else:
            print(f"   Signup failed: {res.status_code} {res.text}")
            sys.exit(1)
    except Exception as e:
        print(f"   Signup error: {e}")
        sys.exit(1)

    # 2. Approve User & Make Admin (Direct DB)
    print("2. Approving user...")
    db = SessionLocal()
    user = db.query(User).filter(User.email == "verify@test.com").first()
    if user:
        user.is_approved = True
        user.is_admin = True
        db.commit()
        print("   User approved and made admin")
    else:
        print("   User not found in DB")
        sys.exit(1)
    db.close()

    # 3. Login
    print("3. Logging in...")
    login_data = {
        "email": "verify@test.com",
        "employee_id": "VERIFY01"
    }
    res = requests.post(f"{API_URL}/auth/login", json=login_data)
    if res.status_code != 200:
        print(f"   Login failed: {res.status_code} {res.text}")
        sys.exit(1)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   Login successful")

    # 4. Create Categories
    print("4. Creating categories...")
    cat1_id = "primary_cat_1"
    cat2_id = "secondary_cat_1"
    
    # Check if exists first (or just ignore error)
    requests.post(f"{API_URL}/categories", json={"name": "P-Cat", "type": "primary"}, headers=headers)
    requests.post(f"{API_URL}/categories", json={"name": "S-Cat", "type": "secondary"}, headers=headers)
    
    # Fetch categories to get IDs
    res = requests.get(f"{API_URL}/categories", headers=headers)
    cats = res.json()
    p_cat_id = cats["primary"][0]["id"]
    s_cat_id = cats["secondary"][0]["id"]
    print(f"   Categories ready: {p_cat_id}, {s_cat_id}")

    # 5. Create Post
    print("5. Creating post...")
    post_data = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "primary_categories": [p_cat_id],
        "secondary_categories": [s_cat_id],
        "memo": "Verification Post"
    }
    res = requests.post(f"{API_URL}/posts", json=post_data, headers=headers)
    if res.status_code == 200:
        print("   Post created successfully!")
        print(res.json())
    else:
        print(f"   Post creation failed: {res.status_code} {res.text}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
