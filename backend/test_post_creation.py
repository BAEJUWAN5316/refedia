import requests
import json

BASE_URL = "http://localhost:8000"

def test_post_creation():
    # 1. Login
    print("🔑 Logging in...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "bae@socialmc.co.ke",
        "employee_id": "TH251110"
    })
    
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.text}")
        return

    token = login_resp.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("✅ Login successful")

    # 2. Get Categories
    print("📂 Fetching categories...")
    cat_resp = requests.get(f"{BASE_URL}/api/categories", headers=headers)
    if cat_resp.status_code != 200:
        print(f"❌ Failed to fetch categories: {cat_resp.text}")
        return
    
    data = cat_resp.json()
    primary = [c["id"] for c in data["primary"]]
    secondary = [c["id"] for c in data["secondary"]]
    
    print(f"✅ Found {len(primary)} primary and {len(secondary)} secondary categories")
    print(f"Primary IDs: {primary}")
    print(f"Secondary IDs: {secondary}")

    # 3. Try to create post
    print("\n📝 Creating post...")
    url = "https://www.youtube.com/watch?v=weDePxQfiMo"
    
    payload = {
        "url": url,
        "primary_categories": [primary[0]],
        "secondary_categories": [secondary[0]],
        "memo": "DF"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/posts",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📊 Response status: {resp.status_code}")
        print(f"Response headers: {dict(resp.headers)}")
        
        try:
            response_json = resp.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response text: {resp.text}")
        
        if resp.status_code == 200:
            print("\n✅ Post created successfully")
        else:
            print(f"\n❌ Post creation failed with status {resp.status_code}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_post_creation()
