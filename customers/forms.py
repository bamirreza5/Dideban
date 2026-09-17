from django import forms

from .models import Customer, FollowUp


PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
ENGLISH_DIGITS = "0123456789"
DIGIT_TRANSLATION = str.maketrans(
    PERSIAN_DIGITS + ARABIC_DIGITS,
    ENGLISH_DIGITS + ENGLISH_DIGITS,
)


class StyledModelForm(forms.ModelForm):
    """Give every form field consistent, accessible frontend classes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            widget = field.field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            else:
                widget.attrs.setdefault("class", "form-control")
            if field.field.required:
                widget.attrs.setdefault("aria-required", "true")


class CustomerForm(StyledModelForm):
    phone = forms.CharField(
        label="شماره تماس",
        max_length=20,
        widget=forms.TextInput(
            attrs={"placeholder": "مثلاً 09121234567", "inputmode": "tel"}
        ),
    )

    class Meta:
        model = Customer
        fields = [
            "name",
            "phone",
            "email",
            "company",
            "status",
            "source",
            "address",
            "description",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "مثلاً علی رضایی"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com"}),
            "company": forms.TextInput(attrs={"placeholder": "نام شرکت یا سازمان"}),
            "address": forms.TextInput(attrs={"placeholder": "نشانی مشتری"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "نیازها و توضیحات تکمیلی..."}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_phone(self):
        phone = self.cleaned_data["phone"].translate(DIGIT_TRANSLATION)
        phone = phone.replace(" ", "").replace("-", "")
        digits = phone[1:] if phone.startswith("+") else phone
        if not digits.isdigit() or not 7 <= len(digits) <= 15:
            raise forms.ValidationError(
                "شماره تلفن باید بین ۷ تا ۱۵ رقم باشد و می‌تواند با + شروع شود."
            )
        if self.user is not None:
            duplicate = Customer.objects.filter(user=self.user, phone=phone)
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError("این شماره تماس قبلاً ثبت شده است.")
        return phone

    def clean_email(self):
        return self.cleaned_data.get("email", "").strip().lower()


class FollowUpForm(StyledModelForm):
    due_at = forms.DateTimeField(
        label="زمان سررسید",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={"type": "datetime-local"},
        ),
    )

    class Meta:
        model = FollowUp
        fields = [
            "customer",
            "title",
            "kind",
            "priority",
            "due_at",
            "notes",
            "completed",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "موضوع تماس یا جلسه"}),
            "notes": forms.Textarea(
                attrs={"rows": 4, "placeholder": "نکات لازم برای این پیگیری..."}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["customer"].queryset = Customer.objects.filter(user=user)
