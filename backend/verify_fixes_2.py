import requests
import sys
import json

API_URL = "http://localhost:8000/api"

def verify():
    # 1. Login
    print("1. Logging in...")
    login_data = {
        "email": "bae@socialmc.co.kr",
        "employee_id": "TH251110"
    }
    res = requests.post(f"{API_URL}/auth/login", json=login_data)
    if res.status_code != 200:
        print(f"   Login failed: {res.status_code} {res.text}")
        sys.exit(1)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   Login successful")

    # 2. Create Post (if not exists, but we'll create one to be sure)
    print("2. Creating post...")
    # Get categories first
    res = requests.get(f"{API_URL}/categories", headers=headers)
    cats = res.json()
    if not cats["primary"] or not cats["secondary"]:
         # Create dummy categories if needed
         requests.post(f"{API_URL}/categories", json={"name": "P-Test", "type": "primary"}, headers=headers)
         requests.post(f"{API_URL}/categories", json={"name": "S-Test", "type": "secondary"}, headers=headers)
         res = requests.get(f"{API_URL}/categories", headers=headers)
         cats = res.json()

    p_cat_id = cats["primary"][0]["id"]
    s_cat_id = cats["secondary"][0]["id"]

    post_data = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "primary_categories": [p_cat_id],
        "secondary_categories": [s_cat_id],
        "memo": "Test Post for Favorites"
    }
    # Try to create, if conflict (409), delete and recreate
    res = requests.post(f"{API_URL}/posts", json=post_data, headers=headers)
    if res.status_code == 200:
        post_id = res.json()["id"]
        print(f"   Post created: {post_id}")
    elif res.status_code == 409:
        print("   Post already exists, deleting to recreate (to ensure ownership)...")
        # Fetch list to find ID
        res = requests.get(f"{API_URL}/posts", headers=headers)
        posts = res.json()
        target = next((p for p in posts if p["url"] == post_data["url"]), None)
        if target:
            requests.delete(f"{API_URL}/posts/{target['id']}", headers=headers)
            print("   Deleted existing post.")
            # Recreate
            res = requests.post(f"{API_URL}/posts", json=post_data, headers=headers)
            if res.status_code == 200:
                post_id = res.json()["id"]
                print(f"   Post recreated: {post_id}")
            else:
                print(f"   Recreation failed: {res.status_code} {res.text}")
                sys.exit(1)
        else:
            print("   Could not find existing post to delete.")
            sys.exit(1)
    else:
        print(f"   Post creation failed: {res.status_code} {res.text}")
        sys.exit(1)

    # 3. Toggle Favorite (Ensure it's favorited)
    print("3. Toggling favorite...")
    # Check current status first
    res = requests.get(f"{API_URL}/posts/{post_id}", headers=headers)
    if not res.json()["is_favorited"]:
        res = requests.post(f"{API_URL}/posts/{post_id}/favorite", headers=headers)
        print(f"   Favorited: {res.json()}")
    else:
        print("   Already favorited.")

    # 4. Verify Detail View
    print("4. Verifying Detail View (is_favorited=True)...")
    res = requests.get(f"{API_URL}/posts/{post_id}", headers=headers)
    detail = res.json()
    if detail["is_favorited"] is True:
        print("   ✅ Detail view correct: is_favorited=True")
    else:
        print(f"   ❌ Detail view incorrect: is_favorited={detail.get('is_favorited')}")
        sys.exit(1)

    # 5. Verify My Posts Filter
    print("5. Verifying My Posts Filter...")
    res = requests.get(f"{API_URL}/posts?my_posts=true", headers=headers)
    my_posts = res.json()
    found = any(p["id"] == post_id for p in my_posts)
    if found:
        print("   ✅ My Posts filter correct: Post found")
    else:
        print("   ❌ My Posts filter incorrect: Post NOT found")
        # Debug: print all my posts
        print(f"   Returned {len(my_posts)} posts.")
        sys.exit(1)

    print("All verifications passed!")

if __name__ == "__main__":
    verify()
