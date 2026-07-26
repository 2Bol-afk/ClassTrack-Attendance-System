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
def admin_dashboard(request):

    total_students = StudentProfile.objects.all().count()
    total_teachers = TeacherProfile.objects.all().count()
    total_parents = ParentProfile.objects.all().count()
    total_subjects = Subject.objects.all().count()
    # Get the 5 most recent attendance records with related student and subject_offering
    recent_attendance_list = Attendance.objects.select_related(
        'student',                 # fetch related student
        'subject_offering__subject' # fetch related subject through SubjectOffering
    ).order_by('-date', '-time')[:8]

    # --- Dropdown Filters ---
    selected_year = request.GET.get('year', '1st')
    selected_subject_id = request.GET.get('subject', None)

    subjects_for_year = SubjectOffering.objects.filter(year=selected_year).values_list(
        'subject__id', 'subject__subject_code'
    ).distinct()

    if selected_subject_id is None and subjects_for_year:
        selected_subject_id = subjects_for_year[0][0]

    attendance_qs = Attendance.objects.filter(
        student__year=selected_year,
        subject_offering__subject_id=selected_subject_id
    )

    status_counts = attendance_qs.values('status').annotate(count=Count('id'))
    data = {'present':0, 'absent':0, 'late':0}
    for item in status_counts:
        data[item['status']] = item['count']

    context = {
        'years': YEAR_LEVELS,
        'selected_year': selected_year,
        'subjects': subjects_for_year,
        'selected_subject_id': int(selected_subject_id) if selected_subject_id else None,
        'attendance_data': data,
        'recent_attendance_list': recent_attendance_list,
        'total_students':total_students,
        'total_parents':total_parents,
        'total_subjects':total_subjects,
        'total_teachers':total_teachers
    }

    return render(request,'dashboard/admindashboard.html', context)
