import requests

API_URL = "http://localhost:8000"
SHORTS_URL = "https://www.youtube.com/shorts/tQ_mIOwlp4k"

def reproduce_error():
    print("Attempting to create post with Shorts URL...")
    
    # Login as admin
    login_resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "bae@socialmc.co.kr",
        "employee_id": "TH251110"
    })
    
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code}")
        return

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Post
    payload = {
        "url": SHORTS_URL,
        "title": "Shorts Test",
        "description": "Testing shorts creation",
        "primary_categories": ["cat1"],
        "secondary_categories": ["cat2"],
        "video_type": "short"
    }
    
    resp = requests.post(f"{API_URL}/api/posts", json=payload, headers=headers)
    
    if resp.status_code == 200:
        print("Success! Post created.")
    else:
        print(f"Failed! Status: {resp.status_code}")
        print(f"Response: {resp.text}")

if __name__ == "__main__":
    reproduce_error()
