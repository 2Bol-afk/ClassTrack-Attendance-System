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
def parent_student_report(request):
    # Filters
    courses = Course.objects.all()
    year_levels = YEAR_LEVEL_CHOICES
    sections = SECTION_CHOICES

    selected_course = request.GET.get('course')
    selected_year = request.GET.get('year')
    selected_section = request.GET.get('section')

    # Base student queryset
    students = StudentProfile.objects.all()
    if selected_course:
        students = students.filter(course__id=selected_course)
    if selected_year:
        students = students.filter(year=selected_year)
    if selected_section:
        students = students.filter(section=selected_section)

    # Get parents who have these students
    parents = ParentProfile.objects.filter(students__in=students).distinct()

    # Annotate filtered children per parent
    student_ids = students.values_list('student_ID', flat=True)
    for parent in parents:
        parent.filtered_children = parent.students.filter(student_ID__in=student_ids)

    context = {
        'parents': parents,
        'courses': courses,
        'year_levels': year_levels,
        'sections': sections,
        'selected_course': selected_course,
        'selected_year': selected_year,
        'selected_section': selected_section,
        'active': 'reports',
    }
    return render(request, 'reports/parent_children_report.html', context)
@login_required
def student_details(request):
    # Filters
    courses = Course.objects.all()
    year_levels = YEAR_LEVEL_CHOICES
    sections = SECTION_CHOICES

    selected_course = request.GET.get('course')
    selected_year = request.GET.get('year')
    selected_section = request.GET.get('section')

    # Base queryset with prefetch for subjects
    students = StudentProfile.objects.select_related('course').prefetch_related('subjects').all()

    if selected_course:
        students = students.filter(course__id=selected_course)
    if selected_year:
        students = students.filter(year=selected_year)
    if selected_section:
        students = students.filter(section=selected_section)

    context = {
        'students': students,
        'courses': courses,
        'year_levels': year_levels,
        'sections': sections,
        'selected_course': selected_course,
        'selected_year': selected_year,
        'selected_section': selected_section,
        'active': 'reports',
    }
    return render(request, 'reports/student_details.html', context)
