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
def student_dashboard(request):
    student = request.user.studentprofile
    subjects = student.subjects.all()

    # Subject filter for chart, stats & recent attendance
    subject_id = request.GET.get('subject')

    # Base queryset: all attendance for this student (will be filtered below)
    attendance_qs = student.attendances.all().select_related(
        'subject_offering__subject'
    )

    # Optional filter by subject
    selected_subject_id = None
    if subject_id:
        try:
            selected_subject = subjects.get(id=subject_id)
            selected_subject_id = selected_subject.id
            offerings = SubjectOffering.objects.filter(subject=selected_subject)
            attendance_qs = attendance_qs.filter(subject_offering__in=offerings)
        except Subject.DoesNotExist:
            selected_subject = None
    else:
        selected_subject = None

    # Totals & stats use the (possibly filtered) attendance_qs so
    # the chart and percentage reflect the current subject filter.
    total_subjects = subjects.count()
    status_counts = attendance_qs.values('status').annotate(count=Count('id'))

    attendance_data = {'present': 0, 'absent': 0, 'late': 0}
    for item in status_counts:
        attendance_data[item['status']] = item['count']

    total_records = attendance_qs.count()
    if total_records > 0:
        attendance_percentage = (attendance_data["present"] / total_records) * 100
    else:
        attendance_percentage = 0

    # Recent attendance (respecting subject filter if any)
    recent_attendance_list = attendance_qs.order_by('-date', '-time')[:10]

    context = {
        'student': student,
        'total_subjects': total_subjects,
        "attendance_data": attendance_data,
        "attendance_percentage": round(attendance_percentage, 1),
        "total_records": total_records,
        'subjects': subjects,
        'selected_subject_id': selected_subject_id,
        'recent_attendance_list': recent_attendance_list,
    }
    return render(request, 'dashboard/student_dashboard.html', context)

@login_required
def student_subjects(request):
    student = request.user.studentprofile
    subjects = student.subjects.all()

    subject_data = []

    for subject in subjects:
        # Get all subject offerings for this subject
        offerings = SubjectOffering.objects.filter(subject=subject)

        # Aggregate attendances across all offerings
        attendances = student.attendances.filter(subject_offering__in=offerings)

        total_classes = attendances.count()
        present_count = attendances.filter(status='present').count()
        absent_count = attendances.filter(status='absent').count()
        late_count = attendances.filter(status='late').count()
        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

        subject_data.append({
            'name': subject.name,
            'total_classes': total_classes,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'attendance_percentage': round(attendance_percentage, 1),
        })

    context = {
        'subjects': subject_data
    }

    return render(request, 'dashboard/student_subjects.html', context)
@login_required
def student_attendance_overview(request):
    student = request.user.studentprofile
    subjects = student.subjects.all()

    # Get filter values from GET request
    subject_id = request.GET.get('subject')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Default end date is today
    if not end_date:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end_date)

    # Default start date is first day of current month
    if not start_date:
        start_date = date.today().replace(day=1)
    else:
        start_date = date.fromisoformat(start_date)

    # Ensure start_date and end_date are strings for template inputs
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()

    # Filter attendance records
    attendance_qs = student.attendances.filter(date__range=[start_date, end_date])
    selected_subject = None
    if subject_id:
        attendance_qs = attendance_qs.filter(subject_offering__subject_id=subject_id)
        selected_subject = subjects.get(id=subject_id)

    context = {
        'subjects': subjects,
        'attendance_records': attendance_qs.order_by('-date', '-time'),
        'selected_subject': selected_subject,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'dashboard/student_attendance_overview.html', context)
