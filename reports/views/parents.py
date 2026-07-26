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
def parent_child_summary(request):
    parent = request.user.parentprofile

    # All children of the parent
    children = parent.students.all()


    # 1️⃣ Selected child
    selected_child_id = request.GET.get("child")

    if selected_child_id:
        child = StudentProfile.objects.get(student_ID=selected_child_id)
    else:
        # Default = first child
        child = children.first()

    # 2️⃣ Selected subject
    selected_subject_id = request.GET.get("subject")

    # All subjects the child is enrolled in
    subjects = child.subjects.all()

    # Get all attendance records for the selected child
    attendance_qs = Attendance.objects.filter(student=child)

    # Apply subject filter if selected
    if selected_subject_id:
        attendance_qs = attendance_qs.filter(subject_offering__subject_id=selected_subject_id)

    # ---- Summary Counts ----
    total_present = attendance_qs.filter(status="present").count()
    total_absent = attendance_qs.filter(status="absent").count()
    total_late = attendance_qs.filter(status="late").count()

    total_records = attendance_qs.count()

    # Attendance % calculation
    if total_records > 0:
        attendance_percent = round((total_present / total_records) * 100, 1)
    else:
        attendance_percent = 0

    # ---- Recent Attendance (last 10 records) ----
    recent_attendance = (
        attendance_qs
        .select_related("subject_offering__subject")
        .order_by("-date")[:10]
    )

    recent_rows = [
        {
            "date": att.date.strftime("%b %d, %Y"),
            "subject": att.subject_offering.subject.name,
            "status": att.status
        }
        for att in recent_attendance
    ]

    # ---- Subject Breakdown ----
    breakdown = []

    for subj in subjects:
        subj_records = attendance_qs.filter(subject_offering__subject=subj)

        present = subj_records.filter(status="present").count()
        absent = subj_records.filter(status="absent").count()
        late = subj_records.filter(status="late").count()

        total = subj_records.count()

        percent = round((present / total) * 100, 1) if total > 0 else 0

        breakdown.append({
            "subject": subj.name,
            "present": present,
            "absent": absent,
            "late": late,
            "percent": percent
        })

    context = {
        "children": children,
        "selected_child": child.student_ID,

        "subjects": subjects,
        "selected_subject": selected_subject_id,

        "total_present": total_present,
        "total_absent": total_absent,
        "total_late": total_late,
        "attendance_percent": attendance_percent,

        "recent_attendance": recent_rows,
        "subject_breakdown": breakdown,
    }

    return render(request, "reports/parent_child_summary.html", context)
@login_required
def parent_attendance_timeline(request):
    parent = request.user.parentprofile
    children = StudentProfile.objects.filter(parents=parent)

    # Selected child
    selected_child_id = request.GET.get('child')
    if selected_child_id:
        child = children.get(student_ID=selected_child_id)
    else:
        child = children.first()  # default to first child

    # Subject filter
    selected_subject = request.GET.get('subject', 'all')

    # Status filter
    status_filter = request.GET.get('status', 'all')

    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base attendance queryset
    attendance_qs = Attendance.objects.filter(student=child)

    if selected_subject != 'all':
        attendance_qs = attendance_qs.filter(subject_offering__subject__id=selected_subject)

    if status_filter != 'all':
        attendance_qs = attendance_qs.filter(status=status_filter)

    if start_date:
        attendance_qs = attendance_qs.filter(date__gte=start_date)
    if end_date:
        attendance_qs = attendance_qs.filter(date__lte=end_date)

    # Subjects for the dropdown
    subjects = child.subjects.all()

    context = {
        'children': children,
        'selected_child': child,
        'attendance': attendance_qs.order_by('-date'),
        'subjects': subjects,
        'selected_subject': selected_subject,
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'reports/attendance_timeline.html', context)
