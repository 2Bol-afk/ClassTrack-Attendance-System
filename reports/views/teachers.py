from academics.models import SubjectOffering, Subject, Attendance, Course
from accounts.constants import YEAR_LEVEL_CHOICES,SECTION_CHOICES
from django.shortcuts import render,redirect
from accounts.models import StudentProfile,ParentProfile,TeacherProfile
from django.db.models import Value, F
from django.db.models.functions import Concat,Coalesce
from django.db.models import Count, Q
from django.http import JsonResponse
from collections import defaultdict
from datetime import datetime,date
from django.contrib.auth.decorators import login_required


SEMESTER_CHOICES = [('1st','1st Semester'),('2nd','2nd Semester')]


@login_required
def teacher_details_report(request):
    courses = Course.objects.all()
    year_levels = StudentProfile._meta.get_field('year').choices
    sections = StudentProfile._meta.get_field('section').choices

    selected_course = request.GET.get('course')
    selected_year = request.GET.get('year')

    teachers_data = []

    teachers = TeacherProfile.objects.all()

    for teacher in teachers:
        # Assigned subjects, filtered by course/year if selected
        subject_offerings = SubjectOffering.objects.filter(teacher=teacher)
        if selected_course:
            subject_offerings = subject_offerings.filter(subject__course_id=selected_course)
        if selected_year:
            subject_offerings = subject_offerings.filter(year=selected_year)

        subjects_info = []

        for so in subject_offerings:
            # Count students in each section
            section_counts = {code: 0 for code, _ in sections}  # initialize
            students_in_subject = StudentProfile.objects.filter(
                subjects=so.subject,
                course=so.subject.course,
                year=so.year
            ).values('section').annotate(count=Count('student_ID'))

            for s in students_in_subject:
                section_counts[s['section']] = s['count']

            subjects_info.append({
                'subject': so.subject,
                'year': so.year,
                'school_year': so.school_year,
                'section_counts': section_counts
            })

        if subjects_info:
            teachers_data.append({
                'teacher': teacher,
                'subjects_info': subjects_info,
                'rowspan': len(subjects_info)
            })

    context = {
        'courses': courses,
        'year_levels': year_levels,
        'sections': sections,
        'selected_course': selected_course,
        'selected_year': selected_year,
        'teachers_data': teachers_data,
    }
    return render(request, 'reports/teacher_details_report.html', context)
