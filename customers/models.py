from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{7,15}$",
    message="شماره تلفن باید بین ۷ تا ۱۵ رقم باشد و می‌تواند با + شروع شود.",
)


class Customer(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "جدید"
        CONTACTED = "contact", "تماس گرفته شده"
        NEGOTIATION = "deal", "در حال مذاکره"
        WON = "done", "تبدیل شده"
        LOST = "lost", "از دست رفته"

    class Source(models.TextChoices):
        REFERRAL = "referral", "معرفی"
        INSTAGRAM = "instagram", "اینستاگرام"
        WEBSITE = "website", "وب‌سایت"
        PHONE = "phone", "تماس ورودی"
        EXHIBITION = "exhibition", "نمایشگاه"
        OTHER = "other", "سایر"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customers",
        verbose_name="مالک پرونده",
    )
    name = models.CharField("نام مشتری", max_length=100)
    phone = models.CharField("شماره تماس", max_length=16, validators=[phone_validator])
    email = models.EmailField("ایمیل", blank=True)
    company = models.CharField("شرکت / سازمان", max_length=100, blank=True)
    status = models.CharField(
        "وضعیت", max_length=20, choices=Status.choices, default=Status.NEW
    )
    source = models.CharField(
        "نحوه آشنایی",
        max_length=20,
        choices=Source.choices,
        default=Source.OTHER,
    )
    address = models.CharField("آدرس", max_length=250, blank=True)
    description = models.TextField("یادداشت", blank=True)
    last_contact = models.DateTimeField("آخرین ارتباط", blank=True, null=True)
    created = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "phone"], name="uniq_customer_phone_per_user"
            )
        ]
        indexes = [
            models.Index(fields=["user", "status"], name="customer_user_status_idx"),
            models.Index(fields=["user", "-created"], name="customer_user_created_idx"),
        ]

    def __str__(self):
        return self.name

    @property
    def initials(self):
        words = self.name.split()
        return "".join(word[0] for word in words[:2]) if words else "؟"

    @property
    def active_projects_count(self):
        return self.projects.filter(status="active").count()

    @property
    def total_contract_value(self):
        return (
            self.projects.exclude(status="cancel").aggregate(
                total=models.Sum("budget")
            )["total"]
            or 0
        )


class FollowUp(models.Model):
    class Kind(models.TextChoices):
        CALL = "call", "تماس تلفنی"
        MEETING = "meeting", "جلسه"
        EMAIL = "email", "ایمیل"
        SITE_VISIT = "visit", "بازدید محل"
        OTHER = "other", "سایر"

    class Priority(models.TextChoices):
        LOW = "low", "کم"
        NORMAL = "normal", "عادی"
        HIGH = "high", "مهم"
        URGENT = "urgent", "فوری"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="followups",
        verbose_name="مشتری",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followups",
        verbose_name="ثبت‌کننده",
    )
    title = models.CharField("عنوان پیگیری", max_length=160)
    kind = models.CharField(
        "نوع پیگیری", max_length=20, choices=Kind.choices, default=Kind.CALL
    )
    priority = models.CharField(
        "اولویت",
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    due_at = models.DateTimeField("زمان سررسید")
    notes = models.TextField("توضیحات", blank=True)
    completed = models.BooleanField("انجام شده", default=False)
    completed_at = models.DateTimeField("زمان انجام", blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        ordering = ["completed", "due_at"]
        verbose_name = "پیگیری"
        verbose_name_plural = "پیگیری‌ها"
        indexes = [
            models.Index(
                fields=["created_by", "completed", "due_at"],
                name="followup_owner_due_idx",
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.customer}"

    def clean(self):
        super().clean()
        if (
            self.customer_id
            and self.created_by_id
            and self.customer.user_id != self.created_by_id
        ):
            raise ValidationError(
                {"created_by": "ثبت‌کننده پیگیری باید مالک پرونده مشتری باشد."}
            )

    def save(self, *args, **kwargs):
        if self.completed and self.completed_at is None:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return not self.completed and self.due_at < timezone.now()
