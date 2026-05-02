# Boshliq va Xodim - Kriptografik Xavfsizlik Tizimi

## Loyiha Haqida

Ushbu tizim kriptografik xavfsizlik tamoyillarini amaliyotda ko'rsatish uchun yaratilgan. 
Tizimda Boshliq muhim sirlarni Shamir sxemasi yordamida 3 ta ulushga bo'lib, xodimlarga yuboradi. 
Xaker roli esa kamida 2 ta ulushni yig'ib sirni qayta tiklashga harakat qiladi.

**Talaba:** Sadullayev Jaxongir, 172-23 guruh

## Texnologiyalar

- Python Flask
- SQLite
- HTML/CSS/JavaScript
- Shamir Secret Sharing
- HMAC-SHA256
- RSA Digital Signatures
- bcrypt Password Hashing

## Rollar Tizimi

### 1. Admin (Boshqaruvchi)
- Login: `Admin`
- Parol: `Parol2005`
- Huquqlar:
  - Barcha foydalanuvchilarni boshqarish
  - Audit jurnalini ko'rish
  - Foydalanuvchilarni o'chirish

### 2. Boshliq
- Birinchi ro'yxatdan o'tgan foydalanuvchi Boshliq bo'ladi
- Huquqlar:
  - Sirlarni 3 ta ulushga bo'lish
  - Ulushlarni xodimlarga yuborish
  - Xabarlarni imzolash (RSA)
  - RSA kalitlarini yaratish

### 3. Xodim
- Oddiy foydalanuvchi
- Huquqlar:
  - O'ziga yuborilgan ulushlarni ko'rish
  - Xabar yuborish va qabul qilish
  - HMAC tekshirish
  - Imzolarni tekshirish

### 4. Xaker
- Maxsus rol
- Huquqlar:
  - Barcha ulushlarni ko'rish
  - 2 yoki 3 ta ulushni birlashtirib sirni qayta tiklash
  - 1 ta ulush bilan sir tiklab bo'lmasligini ko'rsatish

## Foydalanish Qo'llanmasi

### 1. Tizimni Ishga Tushirish

```bash
pip install -r requirements.txt
python app.py
```

Brauzerda ochish: `http://localhost:5000`

### 2. Birinchi Kirish (Admin)

1. "Tizimga kirish" tugmasini bosing
2. Login: `Admin`
3. Parol: `Parol2005`
4. "Boshqaruv" bo'limida foydalanuvchilarni ko'rish mumkin

### 3. Boshliq Ro'yxatdan O'tish

1. "Ro'yxatdan o'tish" sahifasiga o'ting
2. Foydalanuvchi nomini kiriting
3. Kuchli parol kiriting (8+ belgi, katta/kichik harf, raqam, maxsus belgi)
4. Rol sifatida "Boshliq" ni tanlang
5. Ro'yxatdan o'ting

### 4. Xodim va Xaker Yaratish

Boshliq mavjud bo'lgandan keyin:
1. Yangi foydalanuvchi ro'yxatdan o'tkazish
2. Faqat "Xodim" yoki "Xaker" rollari mavjud bo'ladi
3. Kamida 3 ta Xodim va 1 ta Xaker yarating

### 5. Sirni Taqsimlash (Boshliq)

1. Boshliq sifatida tizimga kirish
2. "Sirni taqsimlash" sahifasiga o'tish
3. Sirni kiriting (masalan: "MaxfiyKalit123")
4. Tavsif qo'shing (ixtiyoriy)
5. "Sirni 3 ga bolib yuborish" tugmasini bosing
6. Tizim avtomatik ravishda 3 ta xodimga ulush yuboradi

### 6. Ulushlarni Ko'rish (Xodim)

1. Xodim sifatida kirish
2. "Sirni taqsimlash" sahifasi
3. O'zingizga yuborilgan ulushni ko'rasiz
4. Ulush kriptografik kod ko'rinishida bo'ladi

### 7. Sirni Qayta Tiklash (Xaker)

**2 ta ulush bilan (muvaffaqiyatli):**
1. Xaker sifatida kirish
2. "Sirni taqsimlash" sahifasi
3. 2 ta xodimning ulushini tanlang
4. "Sirni qayta tiklash" tugmasi
5. Sir muvaffaqiyatli tiklanadi

**1 ta ulush bilan (muvaffaqiyatsiz):**
1. Faqat 1 ta ulushni tanlang
2. "Sirni qayta tiklash" tugmasi
3. "Qayta tiklash muvaffaqiyatsiz" xabari chiqadi

### 8. Xabar Yuborish

1. Istalgan foydalanuvchi kirishi
2. "Xabarlar" sahifasi
3. Qabul qiluvchi nomi va xabar matnini kiriting
4. "Yuborish" tugmasi
5. Xabar HMAC-SHA256 bilan avtomatik himoyalanadi

### 9. HMAC Tekshirish

1. Xabarlar ro'yxatida "HMAC tekshir" tugmasi
2. Yashil rang = xabar o'zgarmagan
3. Qizil rang = xabar yaxlitligi buzilgan

### 10. Raqamli Imzo (Boshliq/Admin)

1. Avval "RSA kalitlarini yaratish" kerak
2. Xabar yuborish
3. "Imzolash" tugmasi
4. Boshqa foydalanuvchi "Imzoni tekshir" bilan tasdiqlaydi

### 11. Audit Jurnali (Admin)

1. Admin sifatida kirish
2. "Audit" bo'limi
3. Barcha amallar ro'yxati:
   - Ro'yxatdan o'tish
   - Tizimga kirish/chikish
   - Xabar yuborish
   - HMAC tekshirish
   - Imzo tekshirish
   - Sir bo'lish/tiklash

## Xavfsizlik Xususiyatlari

1. **Parol Xeshlash:** bcrypt algoritmi
2. **Session Boshqaruvi:** Flask secure sessions
3. **HMAC-SHA256:** Xabar yaxlitligi
4. **RSA Imzo:** Raqamli autentifikatsiya
5. **Shamir Secret Sharing:** (2-of-3) taqsimlash
6. **Role-Based Access:** Huquqlar nazorati
7. **Audit Logging:** Barcha amallar kuzatiladi

## Sinov Stsenariysi

### To'liq Test:

1. Admin kirish (Admin/Parol2005)
2. Boshliq ro'yxatdan o'tish (boshliq1/Parol123!)
3. 3 ta Xodim yaratish (xodim1, xodim2, xodim3)
4. 1 ta Xaker yaratish (xaker1)
5. Boshliq kirish → Sirni taqsimlash
6. Har bir xodim kirish → Ulushni ko'rish
7. Xaker kirish → 2 ta ulush bilan tiklash (✅)
8. Xaker kirish → 1 ta ulush bilan tiklash (❌)
9. Xabar yuborish → HMAC tekshirish
10. RSA kalit yaratish → Xabar imzolash → Imzo tekshirish
11. Admin → Audit jurnalini ko'rish

## Muammolarni Hal Qilish

**Database xatosi:**
```bash
rm data.db
python app.py
```

**Port band:**
```bash
# Boshqa portda ishga tushirish
$env:PORT=5001
python app.py
```

**Kalitlar yo'q:**
- Xabarlar sahifasida "RSA kalitlarini yaratish" tugmasini bosing

## Loyiha Tuzilishi

```
TOPSHIRIQ2/
├── app.py                    # Asosiy Flask ilova
├── utils/
│   ├── crypto.py            # Kriptografiya funksiyalari
│   ├── db.py                # Database boshqaruvi
│   └── audit.py             # Audit logging
├── templates/               # HTML shablonlar
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── messages.html
│   ├── secret_sharing.html
│   ├── admin.html
│   └── audit.html
├── static/
│   └── style.css           # Zamonaviy dizayn
├── requirements.txt
├── private.pem             # RSA private key (yaratilgandan keyin)
└── public.pem              # RSA public key (yaratilgandan keyin)
```

## Xulosa

Ushbu loyiha kriptografiyaning amaliy qo'llanilishini ko'rsatadi:
- Sirni taqsimlash va qayta tiklash
- Xabar yaxlitligi (HMAC)
- Raqamli imzolar (RSA)
- Xavfsiz autentifikatsiya
- Rollarga asoslangan huquqlar

Barcha talablar bajarilgan va tizim to'liq ishlaydi.
