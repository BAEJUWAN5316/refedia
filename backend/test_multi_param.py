import requests
import json

def test_multi_param():
    # 1. Login to get token
    login_url = "http://localhost:8000/api/auth/login"
    login_payload = {
        "email": "bae@socialmc.co.ke",
        "employee_id": "1234"
    }
    try:
        login_resp = requests.post(login_url, json=login_payload)
        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.text}")
            return
        token = login_resp.json()["access_token"]
    except Exception as e:
        print(f"Login error: {e}")
        return

    # 2. Send request with multiple primary_category params
    url = "http://localhost:8000/api/posts"
    params = [
        ('primary_category', 'cat1'),
        ('primary_category', 'cat2')
    ]
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Sending request to {url} with params: {params}")
    try:
        resp = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {resp.status_code}")
        # We can't see the server logs directly easily, but if I had modified main.py successfully I could see the response.
        # Since I couldn't modify main.py, I'm relying on the fact that I added print statements earlier.
        # I will check the server logs after this runs.
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_multi_param()
