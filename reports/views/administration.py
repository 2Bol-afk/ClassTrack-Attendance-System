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
def attendance_report(request):
    courses = Course.objects.all()
    year_levels = YEAR_LEVEL_CHOICES
    semesters = SEMESTER_CHOICES
    sections = SECTION_CHOICES

    course = request.GET.get('course')
    year = request.GET.get('year')
    semester = request.GET.get('semester')
    subject = request.GET.get('subject')
    section = request.GET.get('section')

    # Load subjects based on selected course
    subjects = Subject.objects.filter(course__id=course) if course else Subject.objects.all()

    # Base queryset
    report_data = Attendance.objects.select_related(
        'student', 'subject_offering', 'subject_offering__subject'
    )

    # Apply filters
    if course:
        report_data = report_data.filter(student__course__id=course)
    if year:
        report_data = report_data.filter(subject_offering__year=year)
    if semester:
        report_data = report_data.filter(subject_offering__subject__semester_number=semester)
    if subject:
        report_data = report_data.filter(subject_offering__subject__id=subject)
    if section:
        report_data = report_data.filter(student__section=section)

    # Summary
    summary_data = report_data.values(
        'student__student_ID',
        'student__course__name',
    ).annotate(
        full_name=Concat(
            F('student__first_name'),
            Value(' '),
            Coalesce(F('student__middle_name'), Value('')),
            Value(' '),
            F('student__last_name'),
        ),
        total_present=Count('pk', filter=Q(status='present')),
        total_absent=Count('pk', filter=Q(status='absent')),
        total_late=Count('pk', filter=Q(status='late'))
    )

    context = {
        'courses': courses,
        'year_levels': year_levels,
        'semesters': semesters,
        'sections': sections,
        'subjects': subjects,
        'report_data': report_data,
        'summary_data': summary_data,
        'selected_course': course,
        'selected_year': year,
        'selected_semester': semester,
        'selected_subject': subject,
        'selected_section': section,
        'active': 'reports',
    }

    return render(request, 'reports/report.html', context)
