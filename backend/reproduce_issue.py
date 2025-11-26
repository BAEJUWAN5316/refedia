import requests
import json

BASE_URL = "http://localhost:8000"

def reproduce():
    # 1. Login to get token
    print("🔑 Logging in...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "bae@socialmc.co.ke",
        "employee_id": "TH251110"
    })
    
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.text}")
        return

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")

    # 2. Get Categories
    print("📂 Fetching categories...")
    cat_resp = requests.get(f"{BASE_URL}/api/categories", headers=headers)
    if cat_resp.status_code != 200:
        print(f"❌ Failed to fetch categories: {cat_resp.text}")
        return
    
    data = cat_resp.json()
    print(f"Type of response: {type(data)}")
    # print(json.dumps(data, indent=2)) # Debug output

    if isinstance(data, dict):
        # Maybe it returns {primary: [], secondary: []}
        primary = data.get("primary", [])
        secondary = data.get("secondary", [])
        # If list of objects inside
        if primary and isinstance(primary[0], dict):
            primary = [c["id"] for c in primary]
        if secondary and isinstance(secondary[0], dict):
            secondary = [c["id"] for c in secondary]
    elif isinstance(data, list):
        primary = [c["id"] for c in data if c["type"] == "primary"]
        secondary = [c["id"] for c in data if c["type"] == "secondary"]
    else:
        print("❌ Unknown response format")
        return
    
    if not primary or not secondary:
        print("❌ Not enough categories to test")
        print(f"Primary: {primary}")
        print(f"Secondary: {secondary}")
        return

    print(f"✅ Found {len(primary)} primary and {len(secondary)} secondary categories")

    # 3. Try to create post
    print("📝 Creating post...")
    url = "https://www.youtube.com/watch?v=crHHvBDi698"
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/posts",
            headers=headers,
            json={
                "url": url,
                "primary_categories": [primary[0]],
                "secondary_categories": [secondary[0]],
                "memo": "Test memo"
            },
            timeout=60 # Set timeout to 60s
        )
        
        if resp.status_code == 200:
            print("✅ Post created successfully")
            print(resp.json())
        else:
            print(f"❌ Post creation failed: {resp.status_code}")
            print(resp.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    reproduce()
