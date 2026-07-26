from django.db import IntegrityError, transaction
from django.test import TestCase

from academics.models import Course, Semester, Subject


class AcademicModelTests(TestCase):
    def test_semester_is_unique_within_a_school_year(self):
        Semester.objects.create(name="1st", school_year="2026-2027")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Semester.objects.create(name="1st", school_year="2026-2027")

    def test_subject_description_contains_its_academic_identity(self):
        course = Course.objects.create(
            name="BSIT",
            description="Information Technology",
        )
        subject = Subject.objects.create(
            course=course,
            subject_code="IT101",
            name="Introduction to Computing",
            semester_number="1st",
            year_level="1st",
        )

        self.assertEqual(str(subject), "BSIT - IT101 - 1st - 1st")
