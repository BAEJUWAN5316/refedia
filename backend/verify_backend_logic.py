import requests
import sys

API_URL = "http://localhost:8000"

def test_backend_logic():
    print("Starting Backend Logic Verification...")

    # 1. Signup New User
    user_email = "test_script_user@example.com"
    user_emp_id = "TESTSCRIPT01"
    
    print(f"\n[1] Signing up user: {user_email}")
    try:
        resp = requests.post(f"{API_URL}/api/auth/signup", json={
            "email": user_email,
            "name": "Test Script User",
            "employee_id": user_emp_id
        })
        if resp.status_code == 200:
            print("  -> Signup Success")
        elif resp.status_code == 400 and "already registered" in resp.text:
            print("  -> User already exists (Expected if re-running)")
        else:
            print(f"  -> Signup Failed: {resp.status_code} {resp.text}")
            return
    except Exception as e:
        print(f"  -> Request Failed: {e}")
        return

    # 2. Try Login (Should Fail)
    print(f"\n[2] Attempting Login (Should Fail due to unapproved)")
    resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": user_email,
        "employee_id": user_emp_id
    })
    if resp.status_code == 403:
        print("  -> Login Failed as expected (403 Forbidden)")
    else:
        print(f"  -> Unexpected Login Status: {resp.status_code} {resp.text}")
        if resp.status_code == 200:
            print("  -> CRITICAL: Login succeeded but should have failed!")
            return

    # 3. Login as Admin
    print(f"\n[3] Logging in as Admin")
    admin_resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "bae@socialmc.co.kr",
        "employee_id": "TH251110"
    })
    if admin_resp.status_code != 200:
        print(f"  -> Admin Login Failed: {admin_resp.status_code}")
        return
    admin_token = admin_resp.json()["access_token"]
    print("  -> Admin Login Success")

    # 4. Find User ID
    print(f"\n[4] Finding User ID for {user_email}")
    users_resp = requests.get(f"{API_URL}/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    if users_resp.status_code != 200:
        print(f"  -> Failed to fetch users: {users_resp.status_code}")
        return
    
    users = users_resp.json()
    target_user = next((u for u in users if u["email"] == user_email), None)
    if not target_user:
        print("  -> User not found in list")
        return
    user_id = target_user["id"]
    print(f"  -> Found User ID: {user_id}")

    # 5. Approve User
    print(f"\n[5] Approving User {user_id}")
    approve_resp = requests.put(f"{API_URL}/api/admin/users/{user_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    if approve_resp.status_code == 200:
        print("  -> Approval Success")
    else:
        print(f"  -> Approval Failed: {approve_resp.status_code} {approve_resp.text}")
        return

    # 6. Try Login (Should Succeed)
    print(f"\n[6] Attempting Login (Should Succeed)")
    resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": user_email,
        "employee_id": user_emp_id
    })
    if resp.status_code == 200:
        print("  -> Login Success")
    else:
        print(f"  -> Login Failed: {resp.status_code} {resp.text}")
        return

    # 7. Make Admin
    print(f"\n[7] Promoting User to Admin")
    make_admin_resp = requests.put(f"{API_URL}/api/admin/users/{user_id}/make-admin", headers={"Authorization": f"Bearer {admin_token}"})
    if make_admin_resp.status_code == 200:
        print("  -> Make Admin Success")
    else:
        print(f"  -> Make Admin Failed: {make_admin_resp.status_code} {make_admin_resp.text}")
        return

    # 8. Verify Admin Status
    print(f"\n[8] Verifying Admin Status")
    resp = requests.post(f"{API_URL}/api/auth/login", json={
        "email": user_email,
        "employee_id": user_emp_id
    })
    user_data = resp.json()["user"]
    if user_data["is_admin"]:
        print("  -> User is now Admin")
    else:
        print("  -> User is NOT Admin (Failed)")

    print("\nBackend Logic Verification Complete: SUCCESS")

if __name__ == "__main__":
    test_backend_logic()
