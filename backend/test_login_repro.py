import requests
import json

url = "http://localhost:8000/api/auth/login"
payload = {
    "email": "bae@socialmc.co.ke",
    "employee_id": "1234"
}
headers = {
    "Content-Type": "application/json"
}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
