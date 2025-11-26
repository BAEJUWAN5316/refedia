import requests
import time

for i in range(5):
    try:
        print(f"Attempt {i+1}...")
        resp = requests.get("http://localhost:8000/", timeout=2)
        print(f"✅ Server is UP! Status: {resp.status_code}")
        break
    except Exception as e:
        print(f"❌ Server not ready: {e}")
        if i < 4:
            time.sleep(2)
