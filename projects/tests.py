from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from customers.models import Customer

from .models import Project


class ProjectModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("owner")
        self.customer = Customer.objects.create(
            user=self.user, name="مشتری", phone="09121111111"
        )

    def test_financial_properties(self):
        project = Project.objects.create(
            customer=self.customer,
            title="پروژه",
            budget=100_000_000,
            cost=65_000_000,
        )
        self.assertEqual(project.profit, 35_000_000)
        self.assertEqual(str(project.profit_margin), "35.0")

    def test_deadline_cannot_precede_start_date(self):
        today = timezone.localdate()
        project = Project(
            customer=self.customer,
            title="پروژه نامعتبر",
            budget=1,
            cost=0,
            start_date=today,
            deadline=today - timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_done_project_progress_is_forced_to_100(self):
        project = Project.objects.create(
            customer=self.customer,
            title="تحویل شده",
            budget=1,
            cost=0,
            progress=20,
            status=Project.Status.DONE,
        )
        self.assertEqual(project.progress, 100)


class ProjectViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user("owner", password="StrongPass123!")
        self.other_user = User.objects.create_user("other", password="StrongPass123!")
        self.customer = Customer.objects.create(
            user=self.user, name="مشتری من", phone="09121111111"
        )
        self.other_customer = Customer.objects.create(
            user=self.other_user, name="مشتری دیگر", phone="09122222222"
        )
        self.project = Project.objects.create(
            customer=self.customer,
            title="پروژه من",
            budget=12_000_000,
            cost=4_000_000,
        )
        self.other_project = Project.objects.create(
            customer=self.other_customer,
            title="پروژه محرمانه",
            budget=20_000_000,
            cost=7_000_000,
        )

    def test_list_only_displays_owned_projects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("projects:list"))
        self.assertContains(response, self.project.title)
        self.assertNotContains(response, self.other_project.title)

    def test_detail_prevents_cross_user_access(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("projects:detail", args=[self.other_project.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_cannot_create_project_for_another_users_customer(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("projects:create"),
            {
                "customer": self.other_customer.pk,
                "title": "دسترسی غیرمجاز",
                "description": "",
                "budget": 10,
                "cost": 1,
                "progress": 0,
                "status": Project.Status.ACTIVE,
                "start_date": "",
                "deadline": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(title="دسترسی غیرمجاز").exists())
        self.assertIn("customer", response.context["form"].errors)

    def test_csv_export_does_not_leak_other_users_projects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("projects:export"))
        content = response.content.decode("utf-8-sig")
        self.assertIn(self.project.title, content)
        self.assertNotIn(self.other_project.title, content)
