from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="operator", password="StrongPass123!"
        )

    def test_login_page_is_available(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورود به حساب")

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "operator", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 405)
