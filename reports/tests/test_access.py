from django.test import SimpleTestCase
from django.urls import reverse


class ReportAccessTests(SimpleTestCase):
    def test_anonymous_users_are_redirected_from_reports(self):
        route_names = [
            "reports:attendance_report",
            "reports:parent_student_report",
            "reports:student_details_report",
            "reports:teacher_details_report",
            "reports:attendance_overview",
            "reports:attendance_summary",
            "reports:detailed_attendance",
            "reports:parent_child_summary",
            "reports:parent_attendance_report",
        ]

        for route_name in route_names:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("accounts:login")))
