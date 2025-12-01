import requests
import json
from datetime import timedelta
from auth import create_access_token

# 1. Generate Token (Mock)
# We need a valid user in DB. I'll assume user_id=1 exists or I can just mock the token if the backend verifies it against DB.
# Actually, let's just try to hit the endpoint. If I get 401, I'll know.
# But I need the 422 detail.

API_URL = "http://localhost:8000"

# Try to login first to get a real token?
# Or just use a hardcoded token if I can find one.
# I'll try to login as admin if I know the credentials.
# User said "Admin password verification failure" in previous session.
# I'll try to create a token manually using the backend code.

import sys
import os
sys.path.append(os.getcwd())
from database import SessionLocal
from db_models import User

db = SessionLocal()
user = db.query(User).first()
if not user:
    print("No user found")
    sys.exit(1)

access_token = create_access_token(
    data={"sub": user.email, "employee_id": "test"}, # employee_id might be needed
    expires_delta=timedelta(minutes=10)
)
token = access_token

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. Find a post to update
# User mentioned post 26 in the error message.
post_id = 26

# 3. Send PUT request
payload = {
    "title": "Test Update Title",
    "genre_categories": ["1", "2", "3", "4", "5", "6"], # 6 items
    "industry_categories": ["Industry1"]
}

print(f"Sending PUT to {API_URL}/api/posts/{post_id}")
# print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.put(f"{API_URL}/api/posts/{post_id}", headers=headers, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")
print("END")
