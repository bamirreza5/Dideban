from django.urls import path

from . import views


app_name = "customers"

urlpatterns = [
    path("", views.customer_list, name="list"),
    path("new/", views.customer_create, name="create"),
    path("export/", views.customer_export_csv, name="export"),
    path("<int:pk>/", views.customer_detail, name="detail"),
    path("<int:pk>/edit/", views.customer_update, name="update"),
    path("<int:pk>/delete/", views.customer_delete, name="delete"),
    path("followups/", views.followup_list, name="followup_list"),
    path("followups/new/", views.followup_create, name="followup_create"),
    path("followups/<int:pk>/edit/", views.followup_update, name="followup_update"),
    path("followups/<int:pk>/toggle/", views.followup_toggle, name="followup_toggle"),
    path("followups/<int:pk>/delete/", views.followup_delete, name="followup_delete"),
]
