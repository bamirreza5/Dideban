from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import BigIntegerField, Count, ExpressionWrapper, F, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from customers.models import Customer, FollowUp
from projects.models import Project


@login_required
def home(request):
    customers = Customer.objects.filter(user=request.user)
    projects = Project.objects.filter(customer__user=request.user)
    followups = FollowUp.objects.filter(created_by=request.user)

    customer_total = customers.count()
    status_counts = {
        row["status"]: row["count"]
        for row in customers.values("status").annotate(count=Count("id"))
    }
    customer_pipeline = []
    for key, label in Customer.Status.choices:
        count = status_counts.get(key, 0)
        customer_pipeline.append(
            {
                "key": key,
                "label": label,
                "count": count,
                "percent": round(count / customer_total * 100) if customer_total else 0,
            }
        )

    project_total = projects.count()
    project_status_counts = {
        row["status"]: row["count"]
        for row in projects.values("status").annotate(count=Count("id"))
    }
    project_pipeline = []
    for key, label in Project.Status.choices:
        count = project_status_counts.get(key, 0)
        project_pipeline.append(
            {
                "key": key,
                "label": label,
                "count": count,
                "percent": round(count / project_total * 100) if project_total else 0,
            }
        )

    profit_expression = ExpressionWrapper(
        F("budget") - F("cost"), output_field=BigIntegerField()
    )
    financials = projects.exclude(status=Project.Status.CANCELLED).aggregate(
        contract_total=Coalesce(
            Sum("budget"), Value(0), output_field=BigIntegerField()
        ),
        cost_total=Coalesce(Sum("cost"), Value(0), output_field=BigIntegerField()),
        profit_total=Coalesce(
            Sum(profit_expression), Value(0), output_field=BigIntegerField()
        ),
    )

    won_count = status_counts.get(Customer.Status.WON, 0)
    lost_count = status_counts.get(Customer.Status.LOST, 0)
    closed_count = won_count + lost_count
    win_rate = round(won_count / closed_count * 100) if closed_count else 0

    now = timezone.now()
    today = timezone.localdate()
    context = {
        "page_title": "داشبورد",
        "customer_total": customer_total,
        "new_customer_count": status_counts.get(Customer.Status.NEW, 0),
        "project_total": project_total,
        "active_project_count": project_status_counts.get(Project.Status.ACTIVE, 0),
        "open_followup_count": followups.filter(completed=False).count(),
        "overdue_followup_count": followups.filter(
            completed=False, due_at__lt=now
        ).count(),
        "deadline_project_count": projects.filter(
            deadline__gte=today,
            deadline__lte=today + timedelta(days=7),
        )
        .exclude(status__in=[Project.Status.DONE, Project.Status.CANCELLED])
        .count(),
        "win_rate": win_rate,
        "customer_pipeline": customer_pipeline,
        "project_pipeline": project_pipeline,
        "recent_customers": customers[:5],
        "recent_projects": projects.select_related("customer")[:5],
        "upcoming_followups": followups.filter(
            completed=False, due_at__gte=now
        ).select_related("customer")[:6],
        "overdue_followups": followups.filter(
            completed=False, due_at__lt=now
        ).select_related("customer")[:4],
        **financials,
    }
    return render(request, "dashboard/home.html", context)


def error_403(request, exception=None):
    return render(
        request,
        "errors/403.html",
        {"page_title": "دسترسی غیرمجاز"},
        status=403,
    )


def error_404(request, exception=None):
    return render(
        request,
        "errors/404.html",
        {"page_title": "صفحه پیدا نشد"},
        status=404,
    )
