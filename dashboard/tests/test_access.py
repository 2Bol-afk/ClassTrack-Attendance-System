from django.test import SimpleTestCase
from django.urls import reverse


class DashboardAccessTests(SimpleTestCase):
    def test_anonymous_users_are_redirected_from_dashboards(self):
        routes = [
            reverse("dashboard:admin_dashboard"),
            reverse("dashboard:teacher_dashboard"),
            reverse("dashboard:student_dashboard"),
            reverse("dashboard:student_subjects"),
            reverse("dashboard:subject_attendance"),
            reverse("dashboard:dashboard"),
            reverse("dashboard:children_list"),
            reverse("dashboard:student_attendances", args=["STUDENT1"]),
            reverse(
                "dashboard:attendance_detail_subject",
                args=["STUDENT1", "SUBJECT1"],
            ),
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("accounts:login")))
