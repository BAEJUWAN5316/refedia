import requests

API_URL = "http://localhost:8000"
TEST_IMAGE_URL = "https://via.placeholder.com/150"

def test_download_proxy():
    print("Testing Image Download Proxy...")
    
    # Login as admin to get token (endpoint requires approval/login)
    login_resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "bae@socialmc.co.kr",
        "employee_id": "TH251110"
    })
    
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code}")
        return

    token = login_resp.json()["access_token"]
    
    # Test Download
    download_url = f"{API_URL}/api/download/image"
    params = {"url": TEST_IMAGE_URL}
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(download_url, params=params, headers=headers, stream=True)
        
        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "")
            content_length = len(resp.content)
            print(f"Success! Status: 200, Type: {content_type}, Size: {content_length} bytes")
        else:
            print(f"Failed! Status: {resp.status_code}, Detail: {resp.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_download_proxy()
