import requests

BASE_URL = "http://localhost:8000"

def check_health():
    print("💓 Checking server health...")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Root endpoint: {resp.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")

    # Login check
    print("🔑 Logging in...")
    try:
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "bae@socialmc.co.ke",
            "employee_id": "TH251110"
        }, timeout=5)
        
        if login_resp.status_code == 200:
            print("✅ Login successful")
            token = login_resp.json()["access_token"]
            
            # Check /me
            me_resp = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=5)
            print(f"✅ /me endpoint: {me_resp.status_code}")
        else:
            print(f"❌ Login failed: {login_resp.status_code}")
    except Exception as e:
        print(f"❌ Login failed: {e}")

if __name__ == "__main__":
    check_health()
