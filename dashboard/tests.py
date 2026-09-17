from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from customers.models import Customer, FollowUp
from projects.models import Project


class DashboardTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user("owner", password="StrongPass123!")
        other = User.objects.create_user("other", password="StrongPass123!")
        customer = Customer.objects.create(
            user=self.user,
            name="مشتری من",
            phone="09121111111",
            status=Customer.Status.WON,
        )
        other_customer = Customer.objects.create(
            user=other,
            name="مشتری دیگر",
            phone="09122222222",
            status=Customer.Status.WON,
        )
        Project.objects.create(
            customer=customer,
            title="پروژه من",
            budget=100_000,
            cost=40_000,
            status=Project.Status.ACTIVE,
        )
        Project.objects.create(
            customer=other_customer,
            title="پروژه دیگر",
            budget=900_000,
            cost=100_000,
            status=Project.Status.ACTIVE,
        )
        FollowUp.objects.create(
            customer=customer,
            created_by=self.user,
            title="کار عقب افتاده",
            due_at=timezone.now() - timedelta(hours=1),
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_aggregates_only_current_users_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["customer_total"], 1)
        self.assertEqual(response.context["project_total"], 1)
        self.assertEqual(response.context["contract_total"], 100_000)
        self.assertEqual(response.context["profit_total"], 60_000)
        self.assertEqual(response.context["overdue_followup_count"], 1)
