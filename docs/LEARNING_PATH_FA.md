# مسیر آموزشی دقیق پروژه دیدبان CRM

## هدف مسیر

پس از پایان این مسیر باید بتوانید بدون کپی‌کردن کورکورانه:

1. یک پروژه Django را از صفر ساختاربندی کنید.
2. ارتباط Model، Migration، Form، View، URL و Template را توضیح دهید.
3. CRUD چندکاربره و امن بسازید.
4. با ORM جست‌وجو، فیلتر، Aggregate و Annotation انجام دهید.
5. برای رفتارهای حساس تست بنویسید.
6. پروژه را برای انتشار آماده کنید.

زمان پیشنهادی: **۱۴ جلسه ۹۰ تا ۱۲۰ دقیقه‌ای** در چهار هفته. در هر جلسه ابتدا فایل‌های مشخص‌شده را بخوانید، سپس تمرین را انجام دهید و در پایان Checkpoint را اجرا کنید.

---

## جلسه صفر — اجرای سالم و ساخت نقشه ذهنی

**هدف:** پروژه را بدون تغییر اجرا کنید و بدانید هر پوشه چه مسئولیتی دارد.

**بخوانید:**

- `README.md`
- `config/settings.py`
- `config/urls.py`
- این سند تا انتها، بدون تلاش برای حفظ‌کردن جزئیات

**اجرا کنید:**

```bash
python -m venv .venv
# محیط را فعال کنید
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

صفحه‌های Dashboard، Customers، Projects و Follow-ups را باز کنید. یک رکورد بسازید، ویرایش کنید و حذف کنید.

**Checkpoint:** بتوانید پاسخ دهید چرا `manage.py` باید از ریشه پروژه اجرا شود و `INSTALLED_APPS` چه نقشی دارد.

---

## جلسه ۱ — Request، URL و View

**هدف:** مسیر رسیدن یک آدرس مرورگر به تابع Python را درک کنید.

**بخوانید:**

- `config/urls.py`
- `customers/urls.py`
- تابع `customer_list` در `customers/views.py`

**تمرین:** یک View موقت به نام `about` بسازید که Template ساده‌ای را روی `/about/` نمایش دهد. ابتدا URL را در `dashboard/urls.py` اضافه کنید، سپس View و Template را بسازید.

**Checkpoint:**

```bash
python manage.py check
```

بتوانید تفاوت `path()`, `include()` و `name=` را توضیح دهید.

---

## جلسه ۲ — Model و Migration

**هدف:** تفاوت تغییر کد مدل با تغییر واقعی Schema دیتابیس را یاد بگیرید.

**بخوانید:**

- `customers/models.py`
- `customers/migrations/0001_initial.py`
- Migration دوم Customers

**تمرین:** فیلد اختیاری `national_id` را به Customer اضافه کنید. سپس:

```bash
python manage.py makemigrations
python manage.py sqlmigrate customers 0003
python manage.py migrate
```

قبل از `migrate`، SQL تولیدشده را بخوانید.

**Checkpoint:** بتوانید توضیح دهید چرا فایل Migration را بعد از انتشار نباید بی‌دلیل ویرایش کرد.

---

## جلسه ۳ — رابطه‌ها و قواعد دامنه

**هدف:** ForeignKey، Related Name، Choice و Property را عملی یاد بگیرید.

**بخوانید:**

- رابطه `Customer.user`
- رابطه `Project.customer`
- رابطه‌های `FollowUp`
- Propertyهای `profit`, `profit_margin`, `is_overdue`

**تمرین:** در Django Shell این Queryها را بنویسید:

```bash
python manage.py shell
```

```python
from customers.models import Customer
from projects.models import Project

Customer.objects.first().projects.all()
Project.objects.select_related("customer").first().customer.name
```

سپس یک Property به Customer اضافه کنید که تعداد پیگیری‌های باز او را برگرداند.

**Checkpoint:** تفاوت `CASCADE` و `PROTECT` و دلیل انتخاب هرکدام در این پروژه را توضیح دهید.

---

## جلسه ۴ — Django Admin

**هدف:** بدون ساخت UI سفارشی، داده را از پنل مدیریتی کنترل کنید.

**بخوانید:**

- `customers/admin.py`
- `projects/admin.py`

**اجرا کنید:**

```bash
python manage.py createsuperuser
python manage.py runserver
```

به `/admin/` بروید. Search، Filter و Inline پیگیری را امتحان کنید.

**تمرین:** ستون `last_contact` را به `CustomerAdmin.list_display` اضافه کنید.

**Checkpoint:** تفاوت Admin با UI اصلی CRM را توضیح دهید؛ Admin ابزار کارکنان فنی/مدیر است، نه الزاماً رابط نهایی کاربر.

---

## جلسه ۵ — Form و اعتبارسنجی

**هدف:** چرخه Bound/Unbound Form، `is_valid()` و `clean_<field>` را بفهمید.

**بخوانید:**

- `customers/forms.py`
- `projects/forms.py`
- `customer_create`

**تمرین ۱:** در فرم مشتری یک شماره فارسی وارد کنید و بعد مقدار ذخیره‌شده را در Admin ببینید.

**تمرین ۲:** در `CustomerForm` قانونی اضافه کنید که نام کمتر از سه کاراکتر را رد کند.

**Checkpoint:** توضیح دهید چرا `user` داخل `CustomerForm.fields` نیست و مالک در View تنظیم می‌شود.

---

## جلسه ۶ — CRUD کامل

**هدف:** Create، Read، Update و Delete را به‌صورت یک چرخه واحد ببینید.

**بخوانید:**

- توابع CRUD در `customers/views.py`
- `templates/customers/form.html`
- `templates/customers/confirm_delete.html`

**تمرین:** یک موجودیت ساده `Note` برای یادداشت داخلی مشتری بسازید؛ ابتدا Model، سپس Migration، Form، URL، View و Template.

**Checkpoint:** برای هر عملیات مشخص کنید کدام HTTP Method مناسب است. حذف و Toggle باید با POST انجام شوند، نه GET.

---

## جلسه ۷ — احراز هویت و جلوگیری از IDOR

**هدف:** امنیت سطح شیء را یاد بگیرید.

**بخوانید:**

- `accounts/forms.py`
- `accounts/urls.py`
- تمام موارد `@login_required`
- تمام `get_object_or_404(... user=request.user)`ها

**آزمایش دستی:** دو Superuser یا User بسازید. با کاربر اول یک مشتری ثبت کنید، سپس با کاربر دوم تلاش کنید URL عددی همان مشتری را باز کنید. باید 404 دریافت شود.

**تمرین:** تست جدیدی بنویسید که ثابت کند کاربر دوم نمی‌تواند FollowUp کاربر اول را ویرایش کند.

**Checkpoint:** تفاوت Authentication و Authorization را با مثال همین پروژه شرح دهید.

---

## جلسه ۸ — ORM پیشرفته: Search، Filter و Pagination

**هدف:** QuerySet زنجیره‌ای، `Q`، Allowlist مرتب‌سازی و Paginator را یاد بگیرید.

**بخوانید:**

- `_filtered_customers`
- `_filtered_projects`
- `partials/pagination.html`
- Template Tag `url_replace`

**تمرین ۱:** فیلتر «مشتری دارای پروژه فعال» اضافه کنید.

**تمرین ۲:** در Shell خروجی `.query` را ببینید:

```python
queryset, _ = _filtered_customers(request)  # در Debugger یا Test
print(queryset.query)
```

**Checkpoint:** توضیح دهید چرا مقدار خام `sort` نباید مستقیم وارد `order_by()` شود.

---

## جلسه ۹ — Aggregate، Annotation و Dashboard

**هدف:** محاسبه KPI در دیتابیس به‌جای حلقه Python.

**بخوانید:**

- `dashboard/views.py`
- `dashboard/templatetags/crm_extras.py`
- `templates/dashboard/home.html`

**تمرین:** KPI میانگین درصد پیشرفت پروژه‌های فعال را با `Avg("progress")` اضافه کنید.

**Checkpoint:** تفاوت `annotate()` و `aggregate()` را با مثال توضیح دهید:

- Aggregate یک خلاصه برای کل QuerySet می‌دهد.
- Annotation یک مقدار محاسباتی به هر ردیف اضافه می‌کند.

---

## جلسه ۱۰ — Template Inheritance و طراحی RTL

**هدف:** از تکرار HTML جلوگیری کنید و Design System کوچک بسازید.

**بخوانید:**

- `templates/base.html`
- `templates/partials/form_fields.html`
- `static/css/app.css`
- `static/js/app.js`

**تمرین ۱:** یک رنگ جدید برای وضعیت آزمایشی بسازید.

**تمرین ۲:** یک Card جدید بدون Style inline به Dashboard اضافه کنید.

**Checkpoint:** بتوانید نقش `{% extends %}`, `{% block %}`, `{% include %}` و `{% load static %}` را توضیح دهید.

---

## جلسه ۱۱ — تست خودکار

**هدف:** رفتار را تست کنید، نه جزئیات پیاده‌سازی را.

**بخوانید:**

- `customers/tests.py`
- `projects/tests.py`
- `dashboard/tests.py`
- `accounts/tests.py`

**اجرا کنید:**

```bash
python manage.py test --verbosity 2
```

**تمرین:** سه تست اضافه کنید:

1. پروژه با Deadline قبل از Start Date از طریق Form رد شود.
2. CSV فقط رکوردهای مطابق فیلتر را صادر کند.
3. مشتری بدون پروژه قابل حذف باشد.

**Checkpoint:** تمام تست‌ها سبز و تعداد آن‌ها حداقل ۲۴ باشد.

---

## جلسه ۱۲ — تنظیمات، Secret و محیط‌ها

**هدف:** تفاوت Development و Production را درک کنید.

**بخوانید:**

- `config/settings.py`
- `.env.example`
- `.gitignore`

**تمرین:** فایل `.env` بسازید، `DJANGO_DEBUG=false` قرار دهید و سپس اجرا کنید:

```bash
python manage.py check --deploy
```

هشدارها را یکی‌یکی بخوانید و دلیل هرکدام را بنویسید.

**Checkpoint:** بدانید چرا Secret Key، دیتابیس و فایل `.env` نباید وارد Repository عمومی شوند.

---

## جلسه ۱۳ — کارایی و Query Inspection

**هدف:** مشکل N+1 را بشناسید.

**بخوانید:**

- استفاده از `select_related("customer")`
- استفاده از `prefetch_related("projects", "followups")`
- Indexهای Meta در مدل‌ها

**تمرین:** موقتاً `select_related` را حذف کنید و تعداد Queryها را با `django-debug-toolbar` یا `CaptureQueriesContext` مقایسه کنید.

نمونه بدون کتابخانه اضافی:

```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as queries:
    list(Project.objects.select_related("customer")[:10])
print(len(queries))
```

**Checkpoint:** توضیح دهید Index روی چه فیلدهایی سودمند است و چرا Index زیاد نیز هزینه Write را بالا می‌برد.

---

## جلسه ۱۴ — انتشار و پروژه پایانی

**هدف:** یک نسخه قابل تحویل بسازید.

**بخوانید:**

- `docs/DEPLOYMENT_FA.md`

**پروژه پایانی؛ یکی را انتخاب کنید:**

### مسیر A: فاکتور و پرداخت

- مدل Invoice و Payment
- وضعیت پرداخت
- مانده حساب مشتری
- PDF فاکتور

### مسیر B: تیم و سطح دسترسی

- نقش مدیر، فروش و اجرا
- واگذاری Customer و Project به همکار
- Permission و Group
- Audit Log تغییرات

### مسیر C: API و اپ موبایل

- Django REST Framework
- Token Authentication
- Endpointهای Customer و Project
- تست Permissionهای API

**معیار قبولی نهایی:**

- `python manage.py check` بدون خطا
- تمام Migrationها ثبت‌شده
- تمام Testها سبز
- Secret خارج از Git
- داده هر کاربر ایزوله
- README به‌روز
- Backup و Restore یک‌بار آزمایش‌شده

---

## روش مطالعه پیشنهادی کد

برای هر قابلیت، همیشه این ترتیب را دنبال کنید:

```text
URL → View → Form → Model/QuerySet → Template → Test
```

مثلاً برای «ویرایش پروژه»:

1. نام `projects:update` را در Template پیدا کنید.
2. مسیر آن را در `projects/urls.py` ببینید.
3. تابع `project_update` را بخوانید.
4. `ProjectForm` را بررسی کنید.
5. قواعد `Project.clean()` و `save()` را بخوانید.
6. Template فرم را ببینید.
7. یک تست عدم دسترسی کاربر دیگر بنویسید.

این روش مانع گم‌شدن میان فایل‌های Django می‌شود.

## دفترچه پیشرفت

پس از هر جلسه سه جمله ثبت کنید:

1. امروز چه مفهومی را واقعاً فهمیدم؟
2. کدام خطا را خودم حل کردم؟
3. اگر کد را از صفر بنویسم، کدام بخش هنوز برایم مبهم است؟

وقتی بتوانید یک قابلیت کوچک را بدون نگاه‌کردن به نسخه آماده در شش لایه URL، View، Form، Model، Template و Test پیاده کنید، آن مبحث را آموخته‌اید.

