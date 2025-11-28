import requests
import json

BASE_URL = "http://localhost:8000"
EMAIL = "bae@socialmc.co.kr"
EMPLOYEE_ID = "TH251110"

def test_api():
    # 1. Login
    print("🔹 Testing Login...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": EMAIL,
            "employee_id": EMPLOYEE_ID
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Login Successful. Token: {token[:10]}...")
        else:
            print(f"❌ Login Failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Posts
    print("\n🔹 Testing Get Posts...")
    response = requests.get(f"{BASE_URL}/api/posts", headers=headers)
    if response.status_code == 200:
        posts = response.json()
        print(f"✅ Fetched {len(posts)} posts.")
        
        if not posts:
            print("⚠️ No posts found. Creating a test post...")
            create_response = requests.post(f"{BASE_URL}/api/posts", headers=headers, json={
                "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw", # Me at the zoo (first youtube video)
                "primary_categories": ["test"],
                "secondary_categories": [],
                "memo": "Test Post"
            })
            if create_response.status_code == 200:
                print("✅ Test post created.")
                posts = [create_response.json()]
            else:
                print(f"❌ Failed to create test post: {create_response.text}")
                return

        print(f"   First post: {posts[0].get('title')} (Views: {posts[0].get('view_count')})")
        
        # 3. Update View Counts
        print("\n🔹 Testing Update View Counts...")
        response = requests.post(f"{BASE_URL}/api/admin/update-views", headers=headers)
        if response.status_code == 200:
            print(f"✅ Update Views Successful: {response.json()}")
            
            # Fetch again to verify
            response = requests.get(f"{BASE_URL}/api/posts", headers=headers)
            updated_posts = response.json()
            print(f"   Updated View Count: {updated_posts[0].get('view_count')}")
        else:
            print(f"❌ Update Views Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api()
