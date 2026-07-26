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
def class_subject_overview(request):
    teacher = request.user.teacherprofile

    # Filters
    semester = request.GET.get('semester')
    year = request.GET.get('year')
    section = request.GET.get('section')

    offerings = SubjectOffering.objects.filter(teacher=teacher)

    if semester:
        offerings = offerings.filter(subject__semester_number=semester)
    if year:
        offerings = offerings.filter(year=year)

    data = []
    for offering in offerings:
        # Create a list of student counts per section in order of SECTION_CHOICES
        section_counts_list = []
        total_students = 0
        for sec_value, sec_display in SECTION_CHOICES:
            qs = StudentProfile.objects.filter(
                course=offering.subject.course,
                year=offering.year,
                section=sec_value
            )
            # Apply section filter if set
            if section and section != sec_value:
                count = 0
            else:
                count = qs.count()
            section_counts_list.append(count)
            total_students += count

        data.append({
            'subject': offering.subject.name,
            'course': offering.subject.course.name if offering.subject.course else 'N/A',
            'section_counts_list': section_counts_list,
            'total_students': total_students,
            'semester': offering.subject.semester_number,
            'year': offering.year,
            'school_year': offering.school_year,
        })

    context = {
        'data': data,
        'semester_filter': semester,
        'year_filter': year,
        'section_filter': section,
        'semesters': SubjectOffering.objects.values_list('subject__semester_number', flat=True).distinct(),
        'years': SubjectOffering.objects.values_list('year', flat=True).distinct(),
        'sections': SECTION_CHOICES,
        'colspan': 2 + len(SECTION_CHOICES) + 4,
    }
    return render(request, 'reports/class_subject_overview.html', context)
@login_required
def attendance_summary(request):
    teacher = request.user.teacherprofile

    # Filters
    semester = request.GET.get('semester')
    subject_id = request.GET.get('subject')
    section = request.GET.get('section')
    year = request.GET.get('year')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date:
        start_date = date.today().isoformat()
    if not end_date:
        end_date = date.today().isoformat()

    # Get teacher's subject offerings
    offerings = SubjectOffering.objects.filter(teacher=teacher)

    if semester:
        offerings = offerings.filter(subject__semester_number=semester)
    if subject_id:
        offerings = offerings.filter(subject_id=subject_id)
    if year:
        offerings = offerings.filter(year=year)

    data = []
    for offering in offerings:
        # Filter students by course, year, and section
        students_qs = StudentProfile.objects.filter(course=offering.subject.course, year=offering.year)
        if section:
            students_qs = students_qs.filter(section=section)

        total_in_class = students_qs.count()

        # Attendance counts
        attendance_qs = Attendance.objects.filter(subject_offering=offering)
        if start_date and end_date:
            attendance_qs = attendance_qs.filter(date__range=[start_date, end_date])

        if section:
            attendance_qs = attendance_qs.filter(student__section=section)

        present_count = attendance_qs.filter(status='present').count()
        late_count = attendance_qs.filter(status='late').count()
        absent_count = attendance_qs.filter(status='absent').count()

        avg_attendance = 0
        if total_in_class > 0:
            # calculate average %: (present + late)/total *100
            avg_attendance = round((present_count + late_count) / total_in_class * 100, 2)

        data.append({
            'subject': offering.subject.name,
            'course': offering.subject.course.name if offering.subject.course else 'N/A',
            'section': section if section else 'All',
            'total_in_class': total_in_class,
            'avg_attendance': avg_attendance,
            'present': present_count,
            'late': late_count,
            'absent': absent_count,
            'semester': offering.subject.semester_number,
            'year': offering.year,
            'school_year': offering.school_year,
        })

    context = {
        'start_date':start_date,
        'end_date':end_date,
        'data': data,
        'semester_filter': semester,
        'year_filter': year,
        'section_filter': section,
        'subject_filter': subject_id,
        'semesters': SubjectOffering.objects.values_list('subject__semester_number', flat=True).distinct(),
        'years': SubjectOffering.objects.values_list('year', flat=True).distinct(),
        'sections': SECTION_CHOICES,
        'subjects': SubjectOffering.objects.filter(teacher=teacher).values_list('subject__id','subject__name').distinct(),
    }
    return render(request, 'reports/attendance_summary.html', context)

@login_required
def detailed_attendance(request):
    teacher = request.user.teacherprofile

    # Filters
    subject_id = request.GET.get('subject')
    year = request.GET.get('year')
    section = request.GET.get('section')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_name = request.GET.get('search_name', '').strip()

    if not start_date:
        start_date = date.today().isoformat()
    if not end_date:
        end_date = date.today().isoformat()

    # Get teacher's subjects
    offerings = SubjectOffering.objects.filter(teacher=teacher)

    if subject_id:
        offerings = offerings.filter(subject_id=subject_id)
    if year:
        offerings = offerings.filter(year=year)

    # Collect attendance records
    attendance_records = Attendance.objects.filter(subject_offering__in=offerings)

    if section:
        attendance_records = attendance_records.filter(student__section=section)
    if start_date and end_date:
        attendance_records = attendance_records.filter(date__range=[start_date, end_date])
    if search_name:
        attendance_records = attendance_records.filter(
            student__first_name__icontains=search_name
        ) | attendance_records.filter(
            student__last_name__icontains=search_name
        )

    attendance_records = attendance_records.select_related('student', 'subject_offering__subject')

    # Prepare data for template
    data = []
    for record in attendance_records:
        data.append({
            'student': f"{record.student.first_name} {record.student.last_name}",
            'subject': record.subject_offering.subject.name,
            'date': record.date,
            'status': record.status.capitalize()
        })

    # Context
    context = {
        'data': data,
        'subject_filter': subject_id,
        'year_filter': year,
        'section_filter': section,
        'start_date': start_date,
        'end_date': end_date,
        'search_name': search_name,
        'sections': SECTION_CHOICES,
        'years': SubjectOffering.objects.filter(teacher=teacher).values_list('year', flat=True).distinct(),
        'subjects': SubjectOffering.objects.filter(teacher=teacher).values_list('subject__id','subject__name').distinct(),
    }

    return render(request, 'reports/detailed_attendance.html', context)
