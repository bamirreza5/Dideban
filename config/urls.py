"""Top-level URL routing for Dideban CRM."""

from django.contrib import admin
from django.urls import include, path


admin.site.site_header = "مدیریت دیدبان CRM"
admin.site.site_title = "دیدبان CRM"
admin.site.index_title = "پنل مدیریت"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("customers/", include("customers.urls")),
    path("projects/", include("projects.urls")),
    path("", include("dashboard.urls")),
]

handler403 = "dashboard.views.error_403"
handler404 = "dashboard.views.error_404"
