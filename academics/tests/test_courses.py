from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.forms import StudentProfileForm
from academics.models import Course, CourseMajor


class CourseManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='test-password',
            role='admin',
            first_login=False,
        )
        self.client.force_login(self.user)

    def test_course_page_renders_report_icon_and_course_form(self):
        response = self.client.get(reverse('academics:manage_courses'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add a Course')
        self.assertContains(response, 'data-icon="report"')

    def test_add_course_creates_bsed_majors(self):
        response = self.client.post(reverse('academics:add_course'), {
            'name': 'BSED',
            'description': 'Bachelor of Secondary Education',
            'majors': ['English', 'Science', 'Filipino', 'Mathematics'],
        })

        self.assertRedirects(response, reverse('academics:manage_courses'))
        course = Course.objects.get(name='BSED')
        self.assertQuerySetEqual(
            course.majors.values_list('name', flat=True),
            ['English', 'Filipino', 'Mathematics', 'Science'],
        )

    def test_edit_course_reconciles_majors(self):
        course = Course.objects.create(
            name='BSED',
            description='Bachelor of Secondary Education',
        )
        CourseMajor.objects.create(course=course, name='English')
        CourseMajor.objects.create(course=course, name='Science')

        response = self.client.post(
            reverse('academics:edit_course', args=[course.id]),
            {
                'name': 'BSED',
                'description': 'Bachelor of Secondary Education',
                'majors': ['English', 'Filipino'],
            },
        )

        self.assertRedirects(response, reverse('academics:manage_courses'))
        self.assertQuerySetEqual(
            course.majors.values_list('name', flat=True),
            ['English', 'Filipino'],
        )

    def test_major_loader_only_returns_selected_course_majors(self):
        bsed = Course.objects.create(name='BSED', description='Education')
        bsit = Course.objects.create(name='BSIT', description='Technology')
        english = CourseMajor.objects.create(course=bsed, name='English')
        CourseMajor.objects.create(course=bsit, name='Web Development')

        response = self.client.get(
            reverse('academics:load_majors', args=[bsed.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {'majors': [{'id': english.id, 'name': 'English'}]},
        )

    def test_student_form_filters_majors_by_posted_course(self):
        bsed = Course.objects.create(name='BSED', description='Education')
        bsit = Course.objects.create(name='BSIT', description='Technology')
        english = CourseMajor.objects.create(course=bsed, name='English')
        CourseMajor.objects.create(course=bsit, name='Web Development')

        form = StudentProfileForm(data={'course': str(bsed.id)})

        self.assertQuerySetEqual(
            form.fields['major'].queryset,
            [english],
        )
