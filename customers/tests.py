from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from projects.models import Project

from .models import Customer, FollowUp


class CustomerViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user("owner", password="StrongPass123!")
        self.other_user = User.objects.create_user("other", password="StrongPass123!")
        self.customer = Customer.objects.create(
            user=self.user,
            name="مشتری اول",
            phone="09121111111",
            status=Customer.Status.NEW,
            source=Customer.Source.REFERRAL,
        )
        self.other_customer = Customer.objects.create(
            user=self.other_user,
            name="مشتری محرمانه",
            phone="09122222222",
            status=Customer.Status.WON,
            source=Customer.Source.WEBSITE,
        )

    def test_list_requires_authentication(self):
        response = self.client.get(reverse("customers:list"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('customers:list')}",
        )

    def test_list_only_displays_current_users_customers(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:list"))
        self.assertContains(response, self.customer.name)
        self.assertNotContains(response, self.other_customer.name)

    def test_create_assigns_owner_and_normalizes_persian_digits(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("customers:create"),
            {
                "name": "مشتری دوم",
                "phone": "۰۹۱۲-۳۳۳ ۳۳۳۳",
                "email": "TEST@EXAMPLE.COM",
                "company": "شرکت تست",
                "status": Customer.Status.CONTACTED,
                "source": Customer.Source.PHONE,
                "address": "تهران",
                "description": "",
            },
        )
        created = Customer.objects.get(name="مشتری دوم")
        self.assertRedirects(response, reverse("customers:detail", args=[created.pk]))
        self.assertEqual(created.user, self.user)
        self.assertEqual(created.phone, "09123333333")
        self.assertEqual(created.email, "test@example.com")

    def test_duplicate_phone_returns_form_error_instead_of_server_error(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("customers:create"),
            {
                "name": "تکراری",
                "phone": self.customer.phone,
                "status": Customer.Status.NEW,
                "source": Customer.Source.OTHER,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "این شماره تماس قبلاً ثبت شده است")

    def test_customer_detail_prevents_cross_user_access(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("customers:detail", args=[self.other_customer.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_csv_export_does_not_leak_other_users_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:export"))
        content = response.content.decode("utf-8-sig")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.customer.name, content)
        self.assertNotIn(self.other_customer.name, content)

    def test_customer_with_project_cannot_be_deleted(self):
        Project.objects.create(
            customer=self.customer,
            title="پروژه تست",
            budget=10_000_000,
            cost=2_000_000,
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("customers:delete", args=[self.customer.pk])
        )
        self.assertRedirects(
            response, reverse("customers:detail", args=[self.customer.pk])
        )
        self.assertTrue(Customer.objects.filter(pk=self.customer.pk).exists())


class FollowUpTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user("owner", password="StrongPass123!")
        self.other_user = User.objects.create_user("other", password="StrongPass123!")
        self.customer = Customer.objects.create(
            user=self.user, name="مشتری", phone="09121111111"
        )
        self.followup = FollowUp.objects.create(
            customer=self.customer,
            created_by=self.user,
            title="تماس آزمایشی",
            due_at=timezone.now() + timedelta(days=1),
        )

    def test_toggle_marks_followup_complete_and_updates_last_contact(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("customers:followup_toggle", args=[self.followup.pk])
        )
        self.assertRedirects(response, reverse("customers:followup_list"))
        self.followup.refresh_from_db()
        self.customer.refresh_from_db()
        self.assertTrue(self.followup.completed)
        self.assertIsNotNone(self.followup.completed_at)
        self.assertIsNotNone(self.customer.last_contact)

    def test_other_user_cannot_toggle_followup(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("customers:followup_toggle", args=[self.followup.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_toggle_rejects_external_next_redirect(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("customers:followup_toggle", args=[self.followup.pk]),
            {"next": "https://malicious.example/collect"},
        )
        self.assertRedirects(response, reverse("customers:followup_list"))

    def test_followup_owner_must_match_customer_owner(self):
        invalid = FollowUp(
            customer=self.customer,
            created_by=self.other_user,
            title="مالک اشتباه",
            due_at=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            invalid.full_clean()
