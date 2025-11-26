import requests

API_URL = 'http://localhost:8000'

def get_token():
    login_url = f"{API_URL}/api/auth/login"
    payload = {"email": "bae@socialmc.co.ke", "employee_id": "1234"}
    resp = requests.post(login_url, json=payload)
    resp.raise_for_status()
    return resp.json()["access_token"]

def test_debug():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = [
        ("primary_category", "cat1"),
        ("primary_category", "cat2"),
        ("secondary_category", "sec1"),
        ("secondary_category", "sec2"),
    ]
    resp = requests.get(f"{API_URL}/api/debug_posts", params=params, headers=headers)
    print("Status", resp.status_code)
    print("Response", resp.json())

if __name__ == "__main__":
    test_debug()
