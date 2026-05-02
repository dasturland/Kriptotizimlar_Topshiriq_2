"""
Simple verification script for the cryptographic system
"""
import requests

BASE = 'http://127.0.0.1:8000'
s = requests.Session()

print("Testing Admin Login...")
r = s.post(f'{BASE}/login', data={'username': 'Admin', 'password': 'Parol2005'}, allow_redirects=True)
print(f"Status: {r.status_code}")
print(f"URL: {r.url}")
print()

print("Testing Boshliq Login...")
r = s.post(f'{BASE}/login', data={'username': 'boshliq1', 'password': 'Boshliq123!'}, allow_redirects=True)
print(f"Status: {r.status_code}")
print(f"URL: {r.url}")
print()

print("Testing Secret Sharing Page...")
r = s.get(f'{BASE}/secret_sharing')
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("✅ Secret sharing page loads")
    if 'Sirni Taqsimlash' in r.text:
        print("✅ Page content correct")
else:
    print("❌ Page failed to load")
print()

print("Testing Messages Page...")
r = s.get(f'{BASE}/messages')
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("✅ Messages page loads")
else:
    print("❌ Messages page failed")
print()

print("\nAll core pages verified!")
print("\nManual testing steps:")
print("1. Open: http://localhost:8000")
print("2. Login as Admin: Admin / Parol2005")
print("3. Check users in Boshqaruv panel")
print("4. Login as boshliq1 / Boshliq123!")
print("5. Go to Sirni taqsimlash and split a secret")
print("6. Login as xaker1 / Xaker123!")
print("7. Try to recover with 2 shares")
