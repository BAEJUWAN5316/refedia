import requests
import os

BASE_URL = "http://localhost:8000"

def test_api():
    print(f"Testing API at {BASE_URL}")
    
    # 1. Login (if needed, but get_posts might be public? Let's assume public for now or use admin)
    # Actually get_posts is public in app_main.py
    
    # 2. Get Posts
    print("\n🔹 Testing Get Posts...")
    try:
        # Match the failing request params + Add dummy auth header
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{BASE_URL}/api/posts?page=1&limit=20&filter_logic=AND&video_type=&search=&start_date=&end_date=&my_posts=false&favorites_only=false", headers=headers)
        if response.status_code == 200:
            posts = response.json()
            print(f"✅ Fetched {len(posts)} posts.")
        else:
            print(f"❌ Get Posts Failed: {response.status_code}")
            print(f"Response Text: {response.text}")
    except Exception as e:
        print(f"❌ Request Failed: {e}")

if __name__ == "__main__":
    test_api()
