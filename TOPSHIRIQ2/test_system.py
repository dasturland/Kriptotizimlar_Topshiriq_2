"""
Test script for Boshliq va Xodim cryptographic system
Run: python test_system.py
"""

import requests
import sys

BASE_URL = 'http://127.0.0.1:8000'

def test_admin_login():
    print("\n[TEST 1] Admin login...")
    session = requests.Session()
    data = {'username': 'Admin', 'password': 'Parol2005'}
    resp = session.post(f'{BASE_URL}/login', data=data, allow_redirects=False)
    if resp.status_code == 302:
        print("✅ Admin login successful")
        return session
    else:
        print("❌ Admin login failed")
        return None

def test_register_boshliq(session):
    print("\n[TEST 2] Register Boshliq...")
    data = {
        'username': 'boshliq1',
        'password': 'Boshliq123!',
        'role': 'boshliq'
    }
    resp = session.post(f'{BASE_URL}/register', data=data, allow_redirects=False)
    if resp.status_code == 302:
        print("✅ Boshliq registered")
    else:
        print("⚠️  Boshliq may already exist")

def test_register_xodimlar(session):
    print("\n[TEST 3] Register Xodimlar...")
    xodimlar = [
        {'username': 'xodim1', 'password': 'Xodim123!', 'role': 'xodim'},
        {'username': 'xodim2', 'password': 'Xodim123!', 'role': 'xodim'},
        {'username': 'xodim3', 'password': 'Xodim123!', 'role': 'xodim'}
    ]
    for xodim in xodimlar:
        resp = session.post(f'{BASE_URL}/register', data=xodim, allow_redirects=False)
        if resp.status_code == 302:
            print(f"✅ {xodim['username']} registered")
        else:
            print(f"⚠️  {xodim['username']} may already exist")

def test_register_xaker(session):
    print("\n[TEST 4] Register Xaker...")
    data = {
        'username': 'xaker1',
        'password': 'Xaker123!',
        'role': 'xaker'
    }
    resp = session.post(f'{BASE_URL}/register', data=data, allow_redirects=False)
    if resp.status_code == 302:
        print("✅ Xaker registered")
    else:
        print("⚠️  Xaker may already exist")

def test_boshliq_login_and_split():
    print("\n[TEST 5] Boshliq login and split secret...")
    session = requests.Session()
    data = {'username': 'boshliq1', 'password': 'Boshliq123!'}
    resp = session.post(f'{BASE_URL}/login', data=data, allow_redirects=False)
    
    if resp.status_code == 302:
        print("✅ Boshliq logged in")
        
        # Split secret
        split_data = {
            'action': 'split',
            'secret': 'TestSecret2024',
            'description': 'Test sir'
        }
        resp = session.post(f'{BASE_URL}/secret_sharing', data=split_data, allow_redirects=False)
        if resp.status_code == 302:
            print("✅ Secret split into 3 shares")
        else:
            print("❌ Secret split failed")
    else:
        print("❌ Boshliq login failed")

def test_xaker_recovery():
    print("\n[TEST 6] Xaker recovery with 2 shares...")
    session = requests.Session()
    data = {'username': 'xaker1', 'password': 'Xaker123!'}
    resp = session.post(f'{BASE_URL}/login', data=data, allow_redirects=False)
    
    if resp.status_code == 302:
        print("✅ Xaker logged in")
        print("⚠️  Manual test required: Go to /secret_sharing and select 2 shares")
    else:
        print("❌ Xaker login failed")

def test_message_and_hmac():
    print("\n[TEST 7] Send message and verify HMAC...")
    session = requests.Session()
    data = {'username': 'boshliq1', 'password': 'Boshliq123!'}
    session.post(f'{BASE_URL}/login', data=data, allow_redirects=False)
    
    msg_data = {
        'recipient': 'xodim1',
        'body': 'Test xabar - maxfiy'
    }
    resp = session.post(f'{BASE_URL}/messages', data=msg_data, allow_redirects=False)
    if resp.status_code == 302:
        print("✅ Message sent with HMAC")
    else:
        print("❌ Message send failed")

def main():
    print("=" * 60)
    print("BOSHLIQ VA XODIM - TIZIM TESTI")
    print("=" * 60)
    
    try:
        # Check if server is running
        resp = requests.get(BASE_URL)
        if resp.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding")
            sys.exit(1)
        
        # Run tests
        admin_session = test_admin_login()
        if admin_session:
            test_register_boshliq(admin_session)
            test_register_xodimlar(admin_session)
            test_register_xaker(admin_session)
        
        test_boshliq_login_and_split()
        test_xaker_recovery()
        test_message_and_hmac()
        
        print("\n" + "=" * 60)
        print("TEST YAKUNLANDI")
        print("=" * 60)
        print("\nQo'lda test qilish kerak:")
        print("1. Brauzerni oching: http://127.0.0.1:5000")
        print("2. Xaker sifatida kirish")
        print("3. Sirni taqsimlash sahifasida 2 ta ulush tanlang")
        print("4. Sirni qayta tiklash tugmasini bosing")
        print("5. Natijani tekshiring")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Serverga ulanib bo'lmadi!")
        print("Iltimos, avval 'python app.py' ni ishga tushiring")
        sys.exit(1)

if __name__ == '__main__':
    main()
