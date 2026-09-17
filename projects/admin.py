from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "customer",
        "status",
        "progress",
        "budget",
        "cost",
        "deadline",
    )
    list_filter = ("status", "created_at", "deadline")
    search_fields = ("title", "description", "customer__name", "customer__company")
    list_select_related = ("customer", "customer__user")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
