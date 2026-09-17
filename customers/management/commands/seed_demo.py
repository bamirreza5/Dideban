from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from customers.models import Customer, FollowUp
from projects.models import Project


class Command(BaseCommand):
    help = "Create an idempotent demo account with Persian CRM sample data."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo")
        parser.add_argument("--password", default="Demo12345!")
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Reset the password when the demo user already exists.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": "کاربر", "last_name": "آزمایشی"},
        )
        if created or options["reset_password"]:
            user.set_password(password)
            user.save()

        customer_rows = [
            {
                "name": "علیرضا نادری",
                "phone": "09120000001",
                "email": "naderi@example.com",
                "company": "کارخانه سپهر",
                "status": Customer.Status.WON,
                "source": Customer.Source.REFERRAL,
                "address": "تهران، شهرک صنعتی شمس‌آباد",
                "description": "مشتری تجهیزات شبکه و دوربین مداربسته صنعتی.",
            },
            {
                "name": "سارا احمدی",
                "phone": "09120000002",
                "email": "s.ahmadi@example.com",
                "company": "مجتمع آفتاب",
                "status": Customer.Status.NEGOTIATION,
                "source": Customer.Source.INSTAGRAM,
                "address": "تهران، منطقه ۲۲",
                "description": "درخواست بازدید و طراحی سیستم نظارتی مجتمع.",
            },
            {
                "name": "محسن یوسفی",
                "phone": "09120000003",
                "email": "yousefi@example.com",
                "company": "نوآوران داده",
                "status": Customer.Status.CONTACTED,
                "source": Customer.Source.WEBSITE,
                "address": "کرج، عظیمیه",
                "description": "نیازمند بازطراحی رک و کابل‌کشی ساخت‌یافته.",
            },
            {
                "name": "مریم کریمی",
                "phone": "09120000004",
                "email": "karimi@example.com",
                "company": "کلینیک پارس",
                "status": Customer.Status.NEW,
                "source": Customer.Source.PHONE,
                "address": "تهران، سعادت‌آباد",
                "description": "سرنخ جدید؛ بودجه هنوز مشخص نشده است.",
            },
            {
                "name": "امیر رضایی",
                "phone": "09120000005",
                "email": "rezaei@example.com",
                "company": "انبار مرکزی آرمان",
                "status": Customer.Status.WON,
                "source": Customer.Source.EXHIBITION,
                "address": "قزوین، شهر صنعتی البرز",
                "description": "پروژه لینک رادیویی و انتقال تصویر.",
            },
            {
                "name": "نازنین شریفی",
                "phone": "09120000006",
                "email": "sharifi@example.com",
                "company": "فروشگاه زنجیره‌ای بهار",
                "status": Customer.Status.LOST,
                "source": Customer.Source.OTHER,
                "address": "تهران، یوسف‌آباد",
                "description": "به‌دلیل محدودیت بودجه فعلاً متوقف شده است.",
            },
        ]
        customers = {}
        for row in customer_rows:
            phone = row.pop("phone")
            customer, _ = Customer.objects.update_or_create(
                user=user, phone=phone, defaults=row
            )
            customers[phone] = customer

        today = timezone.localdate()
        project_rows = [
            {
                "customer": customers["09120000001"],
                "title": "بازآرایی شبکه و رک کارخانه",
                "description": "اصلاح کابل‌ها، تعویض باکس‌ها، لیبل‌گذاری و سرویس دوربین‌ها.",
                "budget": 480_000_000,
                "cost": 295_000_000,
                "progress": 68,
                "status": Project.Status.ACTIVE,
                "start_date": today - timedelta(days=18),
                "deadline": today + timedelta(days=12),
            },
            {
                "customer": customers["09120000002"],
                "title": "طراحی سیستم نظارتی مجتمع",
                "description": "بازدید اولیه، جانمایی و تهیه پیشنهاد فنی و مالی.",
                "budget": 190_000_000,
                "cost": 110_000_000,
                "progress": 20,
                "status": Project.Status.DRAFT,
                "start_date": today,
                "deadline": today + timedelta(days=25),
            },
            {
                "customer": customers["09120000003"],
                "title": "استانداردسازی کابل‌کشی دفتر",
                "description": "اجرای کابل‌کشی ساخت‌یافته و تست فلوک نقاط شبکه.",
                "budget": 125_000_000,
                "cost": 76_000_000,
                "progress": 35,
                "status": Project.Status.ON_HOLD,
                "start_date": today - timedelta(days=10),
                "deadline": today + timedelta(days=15),
            },
            {
                "customer": customers["09120000005"],
                "title": "لینک رادیویی انتقال تصویر",
                "description": "راه‌اندازی لینک نقطه‌به‌نقطه و تحویل مستندات شبکه.",
                "budget": 240_000_000,
                "cost": 142_000_000,
                "progress": 100,
                "status": Project.Status.DONE,
                "start_date": today - timedelta(days=55),
                "deadline": today - timedelta(days=7),
            },
        ]
        for row in project_rows:
            customer = row.pop("customer")
            title = row.pop("title")
            Project.objects.update_or_create(
                customer=customer, title=title, defaults=row
            )

        now = timezone.now()
        followup_rows = [
            {
                "customer": customers["09120000002"],
                "title": "ارسال پیش‌فاکتور تجهیزات",
                "kind": FollowUp.Kind.EMAIL,
                "priority": FollowUp.Priority.HIGH,
                "due_at": now + timedelta(hours=5),
                "notes": "نسخه نهایی پس از تأیید تعداد دوربین‌ها ارسال شود.",
            },
            {
                "customer": customers["09120000003"],
                "title": "هماهنگی بازدید رک",
                "kind": FollowUp.Kind.SITE_VISIT,
                "priority": FollowUp.Priority.NORMAL,
                "due_at": now + timedelta(days=1, hours=2),
                "notes": "دسترسی اتاق سرور از قبل هماهنگ شود.",
            },
            {
                "customer": customers["09120000004"],
                "title": "تماس برای تکمیل نیازسنجی",
                "kind": FollowUp.Kind.CALL,
                "priority": FollowUp.Priority.URGENT,
                "due_at": now - timedelta(hours=7),
                "notes": "تعداد نقاط شبکه و زمان اجرای موردنظر پرسیده شود.",
            },
            {
                "customer": customers["09120000001"],
                "title": "جلسه گزارش پیشرفت",
                "kind": FollowUp.Kind.MEETING,
                "priority": FollowUp.Priority.HIGH,
                "due_at": now + timedelta(days=3),
                "notes": "گزارش تصویری قبل/بعد آماده شود.",
            },
        ]
        for row in followup_rows:
            customer = row.pop("customer")
            title = row.pop("title")
            FollowUp.objects.update_or_create(
                customer=customer,
                created_by=user,
                title=title,
                defaults=row,
            )

        self.stdout.write(self.style.SUCCESS("Demo CRM data is ready."))
        self.stdout.write(f"Username: {username}")
        if created or options["reset_password"]:
            self.stdout.write(f"Password: {password}")
        else:
            self.stdout.write(
                "Password was not changed (use --reset-password if needed)."
            )
