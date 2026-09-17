from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from customers.models import Customer


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        ACTIVE = "active", "فعال"
        ON_HOLD = "hold", "متوقف"
        DONE = "done", "تمام‌شده"
        CANCELLED = "cancel", "لغوشده"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="مشتری",
    )
    title = models.CharField("نام پروژه", max_length=200)
    description = models.TextField("شرح پروژه", blank=True)
    budget = models.PositiveBigIntegerField("مبلغ قرارداد (تومان)")
    cost = models.PositiveBigIntegerField("هزینه اجرا (تومان)", default=0)
    progress = models.PositiveSmallIntegerField(
        "درصد پیشرفت",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    status = models.CharField(
        "وضعیت", max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    start_date = models.DateField("تاریخ شروع", blank=True, null=True)
    deadline = models.DateField("مهلت تحویل", blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"
        indexes = [
            models.Index(fields=["status", "deadline"], name="project_status_due_idx"),
            models.Index(
                fields=["customer", "-created_at"], name="project_customer_date_idx"
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.start_date and self.deadline and self.deadline < self.start_date:
            raise ValidationError(
                {"deadline": "مهلت تحویل نمی‌تواند قبل از تاریخ شروع باشد."}
            )

    def save(self, *args, **kwargs):
        if self.status == self.Status.DONE:
            self.progress = 100
        super().save(*args, **kwargs)

    @property
    def profit(self):
        return self.budget - self.cost

    @property
    def profit_margin(self):
        if not self.budget:
            return Decimal("0")
        return (Decimal(self.profit) / Decimal(self.budget) * 100).quantize(
            Decimal("0.1")
        )

    @property
    def is_overdue(self):
        return bool(
            self.deadline
            and self.deadline < timezone.localdate()
            and self.status not in {self.Status.DONE, self.Status.CANCELLED}
        )
