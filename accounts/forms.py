from django.contrib.auth.forms import AuthenticationForm


class StyledAuthenticationForm(AuthenticationForm):
    """Authentication form with Persian labels and reusable CSS hooks."""

    error_messages = {
        "invalid_login": "نام کاربری یا رمز عبور صحیح نیست.",
        "inactive": "این حساب کاربری غیرفعال است.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "نام کاربری"
        self.fields["password"].label = "رمز عبور"
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "نام کاربری خود را وارد کنید",
                "autocomplete": "username",
                "autofocus": True,
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "رمز عبور خود را وارد کنید",
                "autocomplete": "current-password",
            }
        )
