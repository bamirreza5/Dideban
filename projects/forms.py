from django import forms

from customers.forms import StyledModelForm
from customers.models import Customer

from .models import Project


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = [
            "customer",
            "title",
            "description",
            "budget",
            "cost",
            "progress",
            "status",
            "start_date",
            "deadline",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً اجرای شبکه کارخانه"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "شرح خدمات و دامنه پروژه..."}
            ),
            "budget": forms.NumberInput(attrs={"min": 0, "step": 1000}),
            "cost": forms.NumberInput(attrs={"min": 0, "step": 1000}),
            "progress": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "start_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "deadline": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["customer"].queryset = Customer.objects.filter(user=user)
