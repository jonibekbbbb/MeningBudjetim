# Shaxsiy xarajatlar hisoblagichi

Django va SQLite asosidagi budjet hisoblagichi. Har bir foydalanuvchi alohida hisob yaratadi; tranzaksiyalar va kategoriyalar uning shaxsiy panelida saqlanadi va boshqa foydalanuvchilarga ko‘rinmaydi.

## Ishga tushirish (Windows, VS Code)

Loyihani VS Code’da ochganingizda VS Code avtomatik ishga tushirish vazifasini tasdiqlashni so‘rashi mumkin. **Allow Automatic Tasks** ni tanlang. U virtual muhitni tayyorlaydi, kerakli kutubxonalarni o‘rnatadi va bazani yangilaydi. Birinchi marta ishga tushganda terminalda lokal admin hisobini yaratish so‘raladi. Keyin server yoqiladi; brauzerda `http://127.0.0.1:8000/` manzilini oching.

Serverni to‘xtatish uchun terminalda `Ctrl+C` bosing. Avtomatik vazifani boshqarish: **Terminal → Configure Tasks**.

## Qo‘lda ishga tushirish (Windows)

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
python manage.py createsuperuser
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

Ma’lumotlar `db.sqlite3` faylida saqlanadi. Ilova ichida **Ro‘yxatdan o‘tish** havolasi orqali har bir kishi o‘z login va parolini yaratadi. Eski umumiy budjet yozuvlari migratsiya vaqtida avvaldan mavjud superuser hisobiga biriktiriladi; superuser bo‘lmasa, tizimga kira olmaydigan `legacy-budget-owner` hisobiga alohida biriktiriladi.

Lokal administrator hisobi kerak bo‘lsa, Django superuser yarating:

```powershell
python manage.py createsuperuser
```

## Render’da demo sifatida joylash

GitHub’dagi repozitoriyni Render’ga ulang va `render.yaml` orqali **Blueprint** yarating. Render so‘raganda `DJANGO_DEPLOY_USERNAME` hamda kuchli `DJANGO_DEPLOY_PASSWORD` qiymatlarini maxfiy environment variable sifatida kiriting. Ilova shaxsiy hisob sahifalarini login bilan himoyalaydi; deploy foydalanuvchisi server ishga tushganda shu qiymatlardan yaratiladi.

Bu sozlama Render’ning bepul web xizmatida SQLite’dan foydalanadi. Bepul xizmatning fayl tizimi doimiy emas: qayta deploy yoki restart paytida tranzaksiyalar va foydalanuvchi ma’lumotlari yo‘qolishi mumkin. Faqat sinov uchun ishlating, haqiqiy moliyaviy ma’lumot kiritmang. Ma’lumotlarni saqlash kerak bo‘lsa, doimiy disk yoki boshqariladigan PostgreSQL bazasi bilan pullik hostingga o‘ting.
