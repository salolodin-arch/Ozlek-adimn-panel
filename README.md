# OZ-LEK Admin Panel — Railway'ga ulash (to'liq qo'llanma)

## Fayllar tarkibi

```
oz-lek-admin-panel/
├── admin_bot.py       ← botning butun mantig'i (mustaqil, o'zi ishga tushadi)
├── database.py        ← SQLite baza (dorilar + kompaniya matni)
├── config.py           ← .env / Railway Variables'dan token o'qiydi
├── requirements.txt
├── railway.json          ← Railway'ning JSON konfiguratsiyasi (build+start buyrug'i)
├── Procfile               ← zaxira (railway.json o'rniga ham ishlaydi)
└── .env.example
```

## 1-qadam — GitHub'ga yuklash

```bash
cd oz-lek-admin-panel
git init
git add .
git commit -m "OZ-LEK admin panel"
git branch -M main
git remote add origin https://github.com/FOYDALANUVCHI_NOMI/oz-lek-admin.git
git push -u origin main
```

## 2-qadam — Railway'da yangi loyiha ochish

1. https://railway.app → **New Project** → **Deploy from GitHub repo**
2. `oz-lek-admin` repo'ingizni tanlang
3. Railway `railway.json` faylini avtomatik topib, undagi sozlamalar bo'yicha ishga tushiradi:
   - Build: **NIXPACKS** (Python'ni o'zi aniqlaydi, `requirements.txt`ni o'rnatadi)
   - Start: `python admin_bot.py`

## 3-qadam — Muhit o'zgaruvchilarini (Variables) qo'shish

Railway loyihangizda **Variables** bo'limiga o'ting va qo'shing:

| Nomi | Qiymati |
|---|---|
| `ADMIN_BOT_TOKEN` | @BotFather'dan olgan tokeningiz |
| `ADMIN_CHAT_ID` | sizning Telegram user ID'ingiz (@userinfobot orqali bilib olasiz) |

`.env` fayl faqat **lokal test** uchun kerak — Railway'da `.env` fayl umuman kerak emas,
chunki tokenlarni shu Variables orqali beradi.

## 4-qadam — Deploy holatini tekshirish

- **Deployments** bo'limida yashil **"Success" / "Active"** yozuvi chiqishi kerak.
- **Logs** bo'limini oching — pastda `Admin bot ishga tushdi...` degan qator ko'rinsa, hammasi joyida.
- Telegramda botingizga `/start` yozing — javob qaytarsa, tugagan.

## Muhim: bazaning saqlanishi haqida

`oz_lek.db` fayli Railway konteyneri ichida saqlanadi. Agar loyihani qayta deploy qilsangiz
(masalan kodni yangilab push qilsangiz), **standart holatda ma'lumotlar o'chib ketishi mumkin**,
chunki konteyner har safar "toza" holatda qayta yaratiladi.

Buning oldini olish uchun Railway'da **Volume** (doimiy xotira) ulashingiz kerak:

1. Loyihangizda **Settings → Volumes → New Volume**
2. Mount path sifatida: `/data` deb yozing
3. `database.py` faylidagi bitta qatorni almashtiring:

```python
# eski:
DB_PATH = "oz_lek.db"

# yangi (Volume ulaganingizdan keyin):
DB_PATH = "/data/oz_lek.db"
```

Shundan keyin ma'lumotlar har qanday qayta deploy qilishda ham saqlanib qoladi.

## Xatolik chiqsa

Railway **Logs** bo'limidagi qizil xatolik matnini menga tashlang — aniq nima xato ekanini
ko'rib, birga tuzataman.
