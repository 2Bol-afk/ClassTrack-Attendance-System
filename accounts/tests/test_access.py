from django.test import SimpleTestCase
from django.urls import reverse


class AccountAccessTests(SimpleTestCase):
    def test_anonymous_users_are_redirected_from_account_management(self):
        route_names = [
            "accounts:manage_teacher",
            "accounts:add_teacher",
            "accounts:manage_student",
            "accounts:add_student",
            "accounts:load_subjects",
            "accounts:manage_parent",
            "accounts:add_parent",
            "accounts:change_password",
            "accounts:accounts_dashboard",
            "accounts:export_accounts_view",
        ]

        for route_name in route_names:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("accounts:login")))
