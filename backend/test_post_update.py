import requests
import json

BASE_URL = "http://localhost:8000"

def test_update_post():
    # 1. Login to get token
    print("🔑 Logging in...")
    try:
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "bae@socialmc.co.kr",
            "employee_id": "TH251110"
        })
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")

        # 2. Create a post first (since DB was reset)
        print("📝 Creating a new post...")
        create_payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "primary_categories": ["먹방"],
            "secondary_categories": ["유머"],
            "memo": "Test post for update"
        }
        create_resp = requests.post(f"{BASE_URL}/api/posts", headers=headers, json=create_payload)
        if create_resp.status_code != 200:
            print(f"❌ Create post failed: {create_resp.text}")
            return
        
        target_post = create_resp.json()
        post_id = target_post["id"]
        print(f"✅ Post created with ID: {post_id}")

        # 3. Update the post
        print(f"📝 Testing update on Post ID: {post_id}")
        update_payload = {
            "title": f"{target_post['title']} (Updated)",
            "primary_categories": target_post["primary_categories"],
            "secondary_categories": target_post["secondary_categories"],
            "memo": "Updated via test script"
        }
        
        print(f"📤 Sending update payload: {json.dumps(update_payload, indent=2)}")
        
        update_resp = requests.put(
            f"{BASE_URL}/api/posts/{post_id}", 
            headers=headers, 
            json=update_payload
        )

        if update_resp.status_code == 200:
            print("✅ Update successful!")
            print(json.dumps(update_resp.json(), indent=2))
        else:
            print(f"❌ Update failed: {update_resp.status_code}")
            try:
                print(json.dumps(update_resp.json(), indent=2))
            except:
                print(update_resp.text)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_update_post()
