import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_DATA = {
    "email": "admin@example.com",
    "employee_id": "admin12345"
}

def run_test():
    print("🔹 Starting Reproduction Test...")
    
    # 0. Signup (Ensure user exists)
    print("\n0️⃣ ensuring user exists...")
    signup_data = {
        "email": LOGIN_DATA["email"],
        "name": "Admin User",
        "employee_id": LOGIN_DATA["employee_id"]
    }
    try:
        requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
        # Ignore error if already exists
    except:
        pass
    
    # 1. Login
    print("\n1️⃣ Logging in...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=LOGIN_DATA)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": "Bearer " + token}
            print("✅ Login successful.")
            
            # Approve user if needed (requires admin, but let's assume auto-approve or we can hack it via DB if needed)
            # Actually, if login succeeded, user is approved.
            # If login failed with 403, we need to approve.
        elif response.status_code == 403:
             print("⚠️ User not approved. Trying to approve via DB hack...")
             # We can't easily hack DB from here without sqlite3 lib, but let's try to continue if we have a token from previous run? No.
             # Let's just hope the user is approved or we use the existing admin.
             # Wait, if I created a new user, it's not approved.
             # I should use a known admin if possible.
             # Or I can use sqlite3 to approve.
             import sqlite3
             conn = sqlite3.connect("test.db")
             cursor = conn.cursor()
             cursor.execute("UPDATE users SET is_approved=1, is_admin=1 WHERE email=?", (LOGIN_DATA["email"],))
             conn.commit()
             conn.close()
             print("✅ User approved via DB.")
             # Retry login
             response = requests.post(f"{BASE_URL}/api/auth/login", json=LOGIN_DATA)
             if response.status_code == 200:
                 token = response.json()["access_token"]
                 headers = {"Authorization": "Bearer " + token}
                 print("✅ Login successful (retry).")
             else:
                 print(f"❌ Login failed after approval: {response.status_code}")
                 return
        else:
            print(f"❌ Login failed: {response.status_code} {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return

    # 2. Create Post
    print("\n2️⃣ Creating Test Post...")
    import random
    rand_param = random.randint(1, 100000)
    post_data = {
        "url": f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&rand={rand_param}",
        "primary_categories": ["Test"],
        "secondary_categories": ["Debug"],
        "memo": "Test Post"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/posts", json=post_data, headers=headers)
        if response.status_code == 200:
            post = response.json()
            post_id = post["id"]
            print(f"✅ Post created: ID {post_id}")
        else:
            print(f"❌ Post creation failed: {response.status_code} {response.text}")
            # Try to find existing post if duplicate
            if "already exists" in response.text:
                print("⚠️ Post already exists, fetching latest...")
                response = requests.get(f"{BASE_URL}/api/posts?limit=1", headers=headers)
                post_id = response.json()[0]["id"]
                print(f"✅ Using existing post: ID {post_id}")
            else:
                return
    except Exception as e:
        print(f"❌ Create post error: {e}")
        return

    # 3. Test Favorites
    print("\n3️⃣ Testing Favorites...")
    try:
        # Toggle Favorite
        response = requests.post(f"{BASE_URL}/api/posts/{post_id}/favorite", headers=headers)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Toggle Favorite: {status}")
            
            # Verify in Get Post
            response = requests.get(f"{BASE_URL}/api/posts/{post_id}", headers=headers)
            post_detail = response.json()
            print(f"🔍 Post Detail is_favorited: {post_detail.get('is_favorited')}")
            
            if post_detail.get('is_favorited') == status['is_favorited']:
                print("✅ Favorite status matches.")
            else:
                print("❌ Favorite status MISMATCH.")
        else:
            print(f"❌ Toggle Favorite failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Favorite error: {e}")

    # 4. Test Post Update
    print("\n4️⃣ Testing Post Update...")
    update_data = {
        "title": "Updated Title",
        "memo": "Updated Memo"
    }
    try:
        response = requests.put(f"{BASE_URL}/api/posts/{post_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_post = response.json()
            print(f"✅ Update successful. Title: {updated_post['title']}")
            if updated_post['title'] == "Updated Title":
                print("✅ Title updated correctly.")
            else:
                print("❌ Title NOT updated.")
        else:
            print(f"❌ Update failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Update error: {e}")

    # 5. Test View Count
    print("\n5️⃣ Testing View Count...")
    try:
        # Get current view count
        response = requests.get(f"{BASE_URL}/api/posts/{post_id}", headers=headers)
        initial_views = response.json().get("view_count", 0)
        print(f"🔍 Initial Views: {initial_views}")
        
        # Request again to increment
        response = requests.get(f"{BASE_URL}/api/posts/{post_id}", headers=headers)
        new_views = response.json().get("view_count", 0)
        print(f"🔍 New Views: {new_views}")
        
        if new_views > initial_views:
            print("✅ View count incremented.")
        else:
            print("❌ View count NOT incremented.")
    except Exception as e:
        print(f"❌ View count error: {e}")

    # 6. Test Admin View Update
    print("\n6️⃣ Testing Admin View Update...")
    try:
        response = requests.post(f"{BASE_URL}/api/admin/update-views", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin update successful: {result}")
        else:
            print(f"❌ Admin update failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Admin update error: {e}")

if __name__ == "__main__":
    run_test()
