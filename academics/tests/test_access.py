from django.test import SimpleTestCase
from django.urls import reverse


class AcademicAccessTests(SimpleTestCase):
    def test_anonymous_users_are_redirected_from_academic_tools(self):
        route_names = [
            "academics:manage_courses",
            "academics:add_course",
            "academics:manage_subjects",
            "academics:add_subject",
            "academics:assign_teacher",
            "academics:add_assignment_page",
            "academics:attendance",
            "academics:student_list",
            "academics:subject_assign",
        ]

        for route_name in route_names:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("accounts:login")))
