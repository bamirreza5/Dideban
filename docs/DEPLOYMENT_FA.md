# راهنمای آماده‌سازی و استقرار

این سند چک‌لیست استقرار است، نه جایگزین تنظیمات اختصاصی سرور. برای استفاده داخلی تک‌کاربره، SQLite کافی است؛ برای تیم چندکاربره یا بار نوشتن هم‌زمان، PostgreSQL انتخاب مناسب‌تری است.

## ۱. بررسی قبل از انتشار

```bash
python manage.py test
python manage.py check
DJANGO_DEBUG=false python manage.py check --deploy
python manage.py makemigrations --check --dry-run
```

هیچ‌کدام نباید خطای حل‌نشده داشته باشند.

## ۲. متغیرهای الزامی

```text
DJANGO_SECRET_KEY=<random-long-secret>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=crm.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://crm.example.com
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SECURE_HSTS_SECONDS=31536000
```

برای تولید Secret Key می‌توانید در محیط امن اجرا کنید:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

کلید تولیدشده را در Log، Git یا پیام عمومی منتشر نکنید.

## ۳. دیتابیس

### SQLite

برای یک کاربر یا Demo مناسب است. پیش از هر انتشار از `db.sqlite3` نسخه پشتیبان بگیرید و مطمئن شوید فرایند وب اجازه نوشتن روی فایل و پوشه آن را دارد.

### PostgreSQL

برای Production تیمی توصیه می‌شود. مراحل مفهومی:

1. نصب PostgreSQL و Driver مناسب Python
2. ساخت Database و User اختصاصی با کمترین Permission
3. انتقال تنظیم `DATABASES` به متغیرهای محیطی
4. اجرای Migration روی دیتابیس جدید
5. آزمایش Restore نسخه پشتیبان

رمز دیتابیس نباید داخل `settings.py` قرار گیرد.

## ۴. Static Files

```bash
python manage.py collectstatic --noinput
```

پوشه `staticfiles/` باید توسط Nginx یا یک Static Middleware معتبر سرو شود. خود `runserver` برای Production نیست.

## ۵. Application Server و HTTPS

- Linux: Gunicorn یا Uvicorn پشت Nginx
- Windows Server: Waitress یا IIS با پیکربندی مناسب
- TLS/HTTPS اجباری
- Reverse Proxy باید Headerهای Host و Scheme را درست منتقل کند
- دسترسی `/admin/` را در صورت امکان به VPN یا IPهای مشخص محدود کنید

نمونه مفهومی Gunicorn:

```bash
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

## ۶. ساخت کاربر اولیه

در Production از `seed_demo` استفاده نکنید. فقط مدیر واقعی بسازید:

```bash
python manage.py createsuperuser
```

اگر قبلاً داده Demo ساخته‌اید، قبل از ورود داده واقعی یک دیتابیس تمیز ایجاد کنید.

## ۷. Backup و Restore

Backup بدون آزمایش Restore قابل اعتماد نیست.

حداقل سیاست پیشنهادی:

- پشتیبان روزانه دیتابیس
- نگهداری هفت نسخه روزانه و چهار نسخه هفتگی
- رمزنگاری فایل Backup
- ذخیره یک نسخه خارج از سرور اصلی
- آزمایش Restore ماهانه

برای SQLite، Backup را هنگامی بگیرید که Write فعال ندارید یا از API استاندارد Backup SQLite استفاده کنید. کپی ساده فایل وسط Write ممکن است ناسازگار شود.

## ۸. Logging و Monitoring

پیش از استفاده واقعی این موارد را اضافه کنید:

- Log خطا در فایل یا سرویس متمرکز
- هشدار خطای 500
- پایش فضای دیسک و سلامت دیتابیس
- ثبت تلاش‌های ورود ناموفق در صورت حساسیت بالا
- Audit Log برای تغییر مبلغ قرارداد و حذف رکورد

## ۹. چک‌لیست نهایی

- [ ] `DEBUG=False`
- [ ] Secret Key تصادفی و خارج از Git
- [ ] Host و CSRF Origin دقیق
- [ ] HTTPS معتبر
- [ ] حساب Demo حذف شده
- [ ] Migration اجرا شده
- [ ] Static جمع‌آوری و سرو می‌شود
- [ ] Backup زمان‌بندی و Restore آزمایش شده
- [ ] سطح دسترسی Admin محدود شده
- [ ] تست مالکیت داده سبز است
- [ ] Log و مانیتورینگ فعال است

