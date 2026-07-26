from django.shortcuts import render, redirect,get_object_or_404

from django.utils import timezone
from accounts.models import TeacherProfile, StudentProfile,ParentProfile
from academics.models import SubjectOffering, Attendance,Subject
from django.db.models import Count, Q
from datetime import datetime, date
from django.contrib.auth.decorators import login_required

# Create your views here.

YEAR_LEVELS = ['1st','2nd','3rd','4th']


@login_required
def teacher_home(request):
    teacher = request.user.teacherprofile

    total_students = StudentProfile.objects.filter(
        subjects__offerings__teacher=teacher
    ).distinct().count()

    total_subjects = SubjectOffering.objects.filter(teacher=teacher).count()
    today = timezone.now().date()
    total_attendance = Attendance.objects.filter(
        subject_offering__teacher=teacher,
        date=today
    ).count()

    # Recent attendance
    recent_attendance_list = Attendance.objects.select_related(
        'student',
        'subject_offering__subject'
    ).filter(subject_offering__teacher=teacher).order_by('-date', '-time')[:5]

    # --- Dropdown Filter for Subjects ---
    selected_subject_id = request.GET.get('subject', None)
    subjects_for_teacher = SubjectOffering.objects.filter(teacher=teacher).values_list(
        'subject__id', 'subject__subject_code'
    ).distinct()

    if selected_subject_id is None and subjects_for_teacher:
        selected_subject_id = subjects_for_teacher[0][0]

    # Attendance overview for selected subject
    attendance_qs = Attendance.objects.filter(
        subject_offering__teacher=teacher,
        subject_offering__subject_id=selected_subject_id
    )

    status_counts = attendance_qs.values('status').annotate(count=Count('id'))
    attendance_data = {'present': 0, 'absent': 0, 'late': 0}
    for item in status_counts:
        attendance_data[item['status']] = item['count']

    context = {
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_attendance': total_attendance,
        'recent_attendance_list': recent_attendance_list,
        'subjects_for_teacher': subjects_for_teacher,
        'selected_subject_id': int(selected_subject_id) if selected_subject_id else None,
        'attendance_data': attendance_data,
    }
    return render(request, 'dashboard/teacherhome.html', context)
