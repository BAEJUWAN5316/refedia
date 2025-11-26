import requests

# 토큰 생성
from auth import create_access_token
token = create_access_token({"sub": "bae@socialmc.co.ke"})

# 게시물 목록 조회
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/posts", headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
