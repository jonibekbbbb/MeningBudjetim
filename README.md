# Shaxsiy xarajatlar hisoblagichi

Django va SQLite asosidagi shaxsiy kirim-chiqim hisoblagichi. Ilova tranzaksiyalarni boshqaradi, balansni hisoblaydi, sanalar va kategoriyalar bo‘yicha filtrlash hamda xarajatlar diagrammasini taqdim etadi.

## Ishga tushirish (Windows)

PowerShell oynasida loyiha papkasiga o‘ting va virtual muhitni faollashtiring:

```powershell
.\.venv\Scripts\Activate.ps1
```

Agar `.venv` mavjud bo‘lmasa, uni yarating:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Kutubxonalarni o‘rnating, ma’lumotlar bazasini tayyorlang va serverni ishga tushiring:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Brauzerda `http://127.0.0.1:8000/` manzilini oching.

## Imkoniyatlar

- Kirim va chiqim tranzaksiyalarini qo‘shish va o‘chirish.
- Jami kirim, jami chiqim va tanlangan davr balansini hisoblash.
- Xarajat kategoriyalarini nom va rang bilan yaratish va o‘chirish.
- Tranzaksiyalarni sana oralig‘i va kategoriya bo‘yicha filtrlash.
- Kategoriyalar bo‘yicha chiqim diagrammasini Django shablonlari va CSS orqali ko‘rish; JavaScript ishlatilmaydi.
- Django admin orqali ma’lumotlarni boshqarish (`/admin/`).

Chiqim uchun kategoriya talab qilinadi; kirimga kategoriya biriktirilmaydi. Tranzaksiyada ishlatilgan kategoriyani o‘chirishga ruxsat berilmaydi.

## Sinovlar

```powershell
python manage.py test
```

Ma’lumotlar `db.sqlite3` faylida saqlanadi. Bu loyiha hozircha lokal, bitta foydalanuvchi foydalanishi uchun mo‘ljallangan; internetga joylashdan oldin autentifikatsiya, maxfiy kalit va production sozlamalarini qo‘shing.
