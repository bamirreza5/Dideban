import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CustomerForm, FollowUpForm
from .models import Customer, FollowUp


def _filtered_customers(request):
    queryset = Customer.objects.filter(user=request.user).annotate(
        project_count=Count("projects", distinct=True)
    )
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    source = request.GET.get("source", "").strip()
    sort = request.GET.get("sort", "newest")

    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(company__icontains=query)
        )
    if status in Customer.Status.values:
        queryset = queryset.filter(status=status)
    if source in Customer.Source.values:
        queryset = queryset.filter(source=source)

    ordering = {
        "newest": "-created",
        "oldest": "created",
        "name": "name",
        "updated": "-updated",
    }
    return queryset.order_by(ordering.get(sort, "-created")), {
        "q": query,
        "selected_status": status,
        "selected_source": source,
        "selected_sort": sort,
    }


@login_required
def customer_list(request):
    queryset, filters = _filtered_customers(request)
    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_title": "مشتریان",
        "page_obj": page_obj,
        "customers": page_obj.object_list,
        "status_choices": Customer.Status.choices,
        "source_choices": Customer.Source.choices,
        **filters,
    }
    return render(request, "customers/list.html", context)


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(
        Customer.objects.filter(user=request.user).prefetch_related(
            "projects", "followups"
        ),
        pk=pk,
    )
    return render(
        request,
        "customers/detail.html",
        {
            "page_title": customer.name,
            "customer": customer,
            "projects": customer.projects.all(),
            "followups": customer.followups.all()[:8],
        },
    )


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        customer = form.save(commit=False)
        customer.user = request.user
        customer.save()
        messages.success(request, "مشتری جدید با موفقیت ثبت شد.")
        return redirect("customers:detail", pk=customer.pk)
    return render(
        request,
        "customers/form.html",
        {"page_title": "مشتری جدید", "form": form, "submit_label": "ثبت مشتری"},
    )


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    form = CustomerForm(request.POST or None, instance=customer, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "اطلاعات مشتری به‌روزرسانی شد.")
        return redirect("customers:detail", pk=customer.pk)
    return render(
        request,
        "customers/form.html",
        {
            "page_title": "ویرایش مشتری",
            "form": form,
            "customer": customer,
            "submit_label": "ذخیره تغییرات",
        },
    )


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    if request.method == "POST":
        if customer.projects.exists():
            messages.error(
                request,
                "این مشتری پروژه ثبت‌شده دارد؛ ابتدا پروژه‌ها را حذف یا منتقل کنید.",
            )
            return redirect("customers:detail", pk=customer.pk)
        customer.delete()
        messages.success(request, "پرونده مشتری حذف شد.")
        return redirect("customers:list")
    return render(
        request,
        "customers/confirm_delete.html",
        {"page_title": "حذف مشتری", "customer": customer},
    )


@login_required
def customer_export_csv(request):
    queryset, _ = _filtered_customers(request)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="customers.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(["نام", "تلفن", "ایمیل", "شرکت", "وضعیت", "منبع", "تاریخ ثبت"])
    for customer in queryset:
        writer.writerow(
            [
                customer.name,
                customer.phone,
                customer.email,
                customer.company,
                customer.get_status_display(),
                customer.get_source_display(),
                timezone.localtime(customer.created).strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return response


@login_required
def followup_list(request):
    followups = FollowUp.objects.filter(created_by=request.user).select_related(
        "customer"
    )
    state = request.GET.get("state", "open")
    priority = request.GET.get("priority", "")
    query = request.GET.get("q", "").strip()

    if state == "done":
        followups = followups.filter(completed=True)
    elif state == "all":
        pass
    elif state == "overdue":
        followups = followups.filter(completed=False, due_at__lt=timezone.now())
    else:
        state = "open"
        followups = followups.filter(completed=False)
    if priority in FollowUp.Priority.values:
        followups = followups.filter(priority=priority)
    if query:
        followups = followups.filter(
            Q(title__icontains=query) | Q(customer__name__icontains=query)
        )

    paginator = Paginator(followups, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "customers/followup_list.html",
        {
            "page_title": "پیگیری‌ها",
            "page_obj": page_obj,
            "followups": page_obj.object_list,
            "selected_state": state,
            "selected_priority": priority,
            "q": query,
            "priority_choices": FollowUp.Priority.choices,
        },
    )


@login_required
def followup_create(request):
    initial = {}
    customer_id = request.GET.get("customer")
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id, user=request.user)
        initial["customer"] = customer
    form = FollowUpForm(request.POST or None, user=request.user, initial=initial)
    if request.method == "POST" and form.is_valid():
        followup = form.save(commit=False)
        followup.created_by = request.user
        followup.save()
        messages.success(request, "پیگیری جدید ثبت شد.")
        return redirect("customers:followup_list")
    return render(
        request,
        "customers/followup_form.html",
        {"page_title": "پیگیری جدید", "form": form, "submit_label": "ثبت پیگیری"},
    )


@login_required
def followup_update(request, pk):
    followup = get_object_or_404(FollowUp, pk=pk, created_by=request.user)
    form = FollowUpForm(request.POST or None, instance=followup, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "پیگیری به‌روزرسانی شد.")
        return redirect("customers:followup_list")
    return render(
        request,
        "customers/followup_form.html",
        {
            "page_title": "ویرایش پیگیری",
            "form": form,
            "followup": followup,
            "submit_label": "ذخیره تغییرات",
        },
    )


@login_required
def followup_toggle(request, pk):
    followup = get_object_or_404(FollowUp, pk=pk, created_by=request.user)
    if request.method != "POST":
        return redirect("customers:followup_list")
    followup.completed = not followup.completed
    followup.save(update_fields=["completed", "completed_at", "updated_at"])
    if followup.completed:
        followup.customer.last_contact = timezone.now()
        followup.customer.save(update_fields=["last_contact", "updated"])
        messages.success(request, "پیگیری به‌عنوان انجام‌شده علامت خورد.")
    else:
        messages.info(request, "پیگیری دوباره به فهرست کارهای باز برگشت.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("customers:followup_list")


@login_required
def followup_delete(request, pk):
    followup = get_object_or_404(FollowUp, pk=pk, created_by=request.user)
    if request.method == "POST":
        followup.delete()
        messages.success(request, "پیگیری حذف شد.")
        return redirect("customers:followup_list")
    return render(
        request,
        "customers/followup_confirm_delete.html",
        {"page_title": "حذف پیگیری", "followup": followup},
    )
