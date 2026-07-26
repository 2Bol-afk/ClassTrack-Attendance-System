from django.test import SimpleTestCase
from django.urls import resolve, reverse

from accounts.views import custom_login


class RootUrlTests(SimpleTestCase):
    def test_root_route_uses_the_class_track_login(self):
        match = resolve("/")

        self.assertIs(match.func, custom_login)
        response = self.client.get("/")
        self.assertContains(response, "ClassTrack Login")

    def test_primary_routes_keep_their_public_paths(self):
        expected_paths = {
            "accounts:login": "/accounts/login/",
            "academics:attendance": "/academic/mark-attendance/",
            "dashboard:admin_dashboard": "/dashboard/admin/",
            "dashboard:teacher_dashboard": "/dashboard/teacher/",
            "dashboard:student_dashboard": "/dashboard/student/",
            "reports:attendance_report": "/reports/admin",
        }

        for route_name, expected_path in expected_paths.items():
            with self.subTest(route=route_name):
                self.assertEqual(reverse(route_name), expected_path)
