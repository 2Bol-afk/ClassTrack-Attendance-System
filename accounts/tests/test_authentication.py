from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from accounts.views import generate_unique_email


class AuthenticationTests(TestCase):
    def test_user_can_sign_in_with_email(self):
        user = CustomUser.objects.create_user(
            username="admin-user",
            email="admin@example.com",
            password="strong-test-password",
            role="admin",
            first_login=False,
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"email": user.email, "password": "strong-test-password"},
        )

        self.assertRedirects(
            response,
            reverse("dashboard:admin_dashboard"),
            fetch_redirect_response=False,
        )

    def test_generated_account_identity_avoids_existing_values(self):
        CustomUser.objects.create_user(
            username="ada.lovelace",
            email="ada.lovelace@css.com",
            password="strong-test-password",
            role="teacher",
        )

        email, username = generate_unique_email("Ada", "Lovelace")

        self.assertEqual(email, "ada.lovelace1@css.com")
        self.assertEqual(username, "ada.lovelace1")
