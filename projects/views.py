import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from customers.models import Customer

from .forms import ProjectForm
from .models import Project


def _filtered_projects(request):
    queryset = Project.objects.filter(customer__user=request.user).select_related(
        "customer"
    )
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    sort = request.GET.get("sort", "newest")

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(customer__name__icontains=query)
            | Q(customer__company__icontains=query)
        )
    if status in Project.Status.values:
        queryset = queryset.filter(status=status)

    ordering = {
        "newest": "-created_at",
        "deadline": "deadline",
        "budget_high": "-budget",
        "progress": "-progress",
        "name": "title",
    }
    return queryset.order_by(ordering.get(sort, "-created_at")), {
        "q": query,
        "selected_status": status,
        "selected_sort": sort,
    }


@login_required
def project_list(request):
    queryset, filters = _filtered_projects(request)
    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/list.html",
        {
            "page_title": "پروژه‌ها",
            "page_obj": page_obj,
            "projects": page_obj.object_list,
            "status_choices": Project.Status.choices,
            **filters,
        },
    )


@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("customer"),
        pk=pk,
        customer__user=request.user,
    )
    return render(
        request,
        "projects/detail.html",
        {"page_title": project.title, "project": project},
    )


@login_required
def project_create(request):
    initial = {}
    customer_id = request.GET.get("customer")
    if customer_id:
        initial["customer"] = get_object_or_404(
            Customer, pk=customer_id, user=request.user
        )
    form = ProjectForm(request.POST or None, user=request.user, initial=initial)
    if request.method == "POST" and form.is_valid():
        project = form.save()
        messages.success(request, "پروژه جدید با موفقیت ثبت شد.")
        return redirect("projects:detail", pk=project.pk)
    return render(
        request,
        "projects/form.html",
        {"page_title": "پروژه جدید", "form": form, "submit_label": "ثبت پروژه"},
    )


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk, customer__user=request.user)
    form = ProjectForm(request.POST or None, instance=project, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "اطلاعات پروژه به‌روزرسانی شد.")
        return redirect("projects:detail", pk=project.pk)
    return render(
        request,
        "projects/form.html",
        {
            "page_title": "ویرایش پروژه",
            "form": form,
            "project": project,
            "submit_label": "ذخیره تغییرات",
        },
    )


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, customer__user=request.user)
    if request.method == "POST":
        project.delete()
        messages.success(request, "پروژه حذف شد.")
        return redirect("projects:list")
    return render(
        request,
        "projects/confirm_delete.html",
        {"page_title": "حذف پروژه", "project": project},
    )


@login_required
def project_export_csv(request):
    queryset, _ = _filtered_projects(request)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="projects.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(
        [
            "پروژه",
            "مشتری",
            "وضعیت",
            "پیشرفت",
            "مبلغ قرارداد",
            "هزینه",
            "سود",
            "مهلت تحویل",
        ]
    )
    for project in queryset:
        writer.writerow(
            [
                project.title,
                project.customer.name,
                project.get_status_display(),
                project.progress,
                project.budget,
                project.cost,
                project.profit,
                project.deadline.isoformat() if project.deadline else "",
            ]
        )
    return response
