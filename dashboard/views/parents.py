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
def children_list(request):
    parent = request.user.parentprofile
    children = parent.students.all()

    context = {
        'children': children
    }
    return render(request, 'dashboard/children_list.html', context)

@login_required
def parent_dashboard(request):
    parent = request.user.parentprofile
    children = parent.students.all()

    selected_child_id = request.GET.get('child')
    selected_subject_id = request.GET.get('subject')
    selected_child = None
    attendance_data = {'present': 0, 'absent': 0, 'late': 0}
    total_subjects = 0
    subjects = []
    recent_attendance_list = []

    if selected_child_id:
        selected_child = children.filter(student_ID=selected_child_id).first()
    elif children.exists():
        selected_child = children.first()

    if selected_child:
        subjects = selected_child.subjects.all()
        total_subjects = subjects.count()

        # Filter attendance by subject if selected
        attendances = selected_child.attendances.all()
        if selected_subject_id:
            attendances = attendances.filter(subject_offering__subject__id=selected_subject_id)

        attendance_data['present'] = attendances.filter(status='present').count()
        attendance_data['absent'] = attendances.filter(status='absent').count()
        attendance_data['late'] = attendances.filter(status='late').count()

        total_classes = attendances.count()
        attendance_percentage = round((attendance_data['present'] / total_classes) * 100, 2) if total_classes > 0 else 0

        # Get recent 10 attendance records
        recent_attendance_list = attendances.order_by('-date')[:10]

    else:
        attendance_percentage = 0

    context = {
        'children': children,
        'selected_child': selected_child,
        'attendance_data': attendance_data,
        'attendance_percentage': attendance_percentage,
        'total_subjects': total_subjects,
        'subjects': subjects,
        'selected_child_id': selected_child_id,
        'selected_subject_id': selected_subject_id,
        'recent_attendance_list': recent_attendance_list,
    }

    return render(request, 'dashboard/parent_dashboard.html', context)




@login_required
def attendance_detail_per_subject(request, student_id, subject_id):
    student = get_object_or_404(StudentProfile, student_ID=student_id)
    subject = get_object_or_404(student.subjects, id=subject_id)

    # Date range filter
    start_date = request.GET.get('start_date') or None
    end_date = request.GET.get('end_date') or timezone.now().date()

    # Get all offerings for this subject
    offerings = SubjectOffering.objects.filter(subject=subject)
    attendances = student.attendances.filter(subject_offering__in=offerings)

    if start_date:
        attendances = attendances.filter(date__range=[start_date, end_date])

    # Summary stats
    total_classes = attendances.count()
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

    context = {
        'student': student,
        'subject': subject,
        'attendance_records': attendances.order_by('date', 'time'),
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'attendance_percentage': round(attendance_percentage, 1),
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'parent/attendance_detail_subject.html', context)

@login_required
def parent_student_attendance_overview(request, student_id):
    student = get_object_or_404(StudentProfile, student_ID=student_id)

    # Subjects dropdown
    subjects = student.subjects.all()
    selected_subject_id = request.GET.get('subject')

    # Always default BOTH to today's date
    today = timezone.now().date()

    start_date = request.GET.get('start_date') or today
    end_date = request.GET.get('end_date') or today

    # Filter logic
    if selected_subject_id:
        selected_subject = subjects.get(id=selected_subject_id)
        offerings = SubjectOffering.objects.filter(subject=selected_subject)
        attendance_records = student.attendances.filter(
            subject_offering__in=offerings,
            date__range=[start_date, end_date]
        )
    else:
        selected_subject = None
        attendance_records = student.attendances.filter(
            date__range=[start_date, end_date]
        )

    context = {
        'student': student,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'start_date': start_date,
        'end_date': end_date,
        'attendance_records': attendance_records.order_by('date', 'time'),
    }
    return render(request, 'dashboard/attendance_overview.html', context)
