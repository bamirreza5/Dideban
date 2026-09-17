from django.contrib import admin

from .models import Customer, FollowUp


class FollowUpInline(admin.TabularInline):
    model = FollowUp
    extra = 0
    fields = ("title", "kind", "priority", "due_at", "completed", "created_by")
    readonly_fields = ()


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "company",
        "status",
        "source",
        "user",
        "created",
    )
    list_filter = ("status", "source", "created")
    search_fields = ("name", "phone", "email", "company")
    list_select_related = ("user",)
    ordering = ("-created",)
    inlines = (FollowUpInline,)


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "customer",
        "kind",
        "priority",
        "due_at",
        "completed",
        "created_by",
    )
    list_filter = ("completed", "priority", "kind", "due_at")
    search_fields = ("title", "customer__name", "customer__phone")
    list_select_related = ("customer", "created_by")
    date_hierarchy = "due_at"
