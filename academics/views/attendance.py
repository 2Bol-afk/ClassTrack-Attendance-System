# views.py


from ..forms import SubjectForm, AssignSubjectForm
from ..models import Subject, Course, SubjectOffering, Attendance
from accounts.models import TeacherProfile, StudentProfile
from django.utils import timezone
from datetime import datetime, date
from django.contrib import messages
from django.db.models import Count, Q
import calendar
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.constants import YEAR_LEVEL_CHOICES, SECTION_CHOICES

# -------------------------------
# Manage Subjects
# -------------------------------


@login_required
def mark_attendance(request):
    teacher = request.user.teacherprofile

    # GET filters
    offering_id = request.GET.get('offering')
    section = request.GET.get('section')
    year = request.GET.get('year')
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    if not selected_date:
        selected_date = date.today().isoformat()
    if not selected_time:
        selected_time = datetime.now().strftime("%H:%M")
    # All offerings assigned to this teacher (hard filter)
    offerings = SubjectOffering.objects.filter(teacher=teacher)
    selected_offering = None
    students = StudentProfile.objects.none()  # default empty queryset

    if offering_id:
        # Only allow access to offerings that belong to this teacher
        selected_offering = get_object_or_404(
            SubjectOffering, id=offering_id, teacher=teacher
        )

        # Default filters to the offering's year/section if not explicitly chosen
        if not year:
            year = selected_offering.year
        if not section:
            section = selected_offering.section

        # Filter students by course + year + section
        students = StudentProfile.objects.filter(
            course=selected_offering.subject.course,
            year=year,
            section=section,
        )

        # Get existing attendance for pre-selection
        if selected_date and selected_time:
            existing_records = Attendance.objects.filter(
                subject_offering=selected_offering,
                date=selected_date
            )
            existing_attendance = {a.student.student_ID: a.status for a in existing_records}
            for student in students:
                student.attendance_status = existing_attendance.get(student.student_ID, '')
        else:
            for student in students:
                student.attendance_status = ''

    # Sections and years for dropdowns – limited strictly to this teacher's offerings
    sections = (
        SubjectOffering.objects.filter(teacher=teacher)
        .values_list('section', flat=True)
        .distinct()
    )
    years = (
        SubjectOffering.objects.filter(teacher=teacher)
        .values_list('year', flat=True)
        .distinct()
    )

    context = {
        'offerings': offerings,
        'selected_offering': selected_offering,
        'students': students,
        'sections': sections,
        'years': years,
        'selected_section': section,
        'selected_year': year,
        'selected_date': selected_date,
        'selected_time': selected_time,
    }

    # POST: Save attendance
    if request.method == 'POST' and selected_offering and selected_date and selected_time:
        for student in students:
            status = request.POST.get(f'status_{student.student_ID}')
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    subject_offering=selected_offering,
                    date=selected_date,  # unique_together field
                    defaults={
                        'status': status,
                        'time': selected_time
                    }
                )
        messages.success(request, "Attendance has been successfully recorded!")
        return redirect(
            request.path
            + f"?offering={offering_id}&section={section or ''}&year={year or ''}&date={selected_date}&time={selected_time}"
        )

    return render(request, 'dashboard/attendance.html', context)


@login_required
def student_list(request):
    teacher = request.user.teacherprofile

    # Get all offerings for this teacher
    offerings = SubjectOffering.objects.filter(teacher=teacher).select_related(
        'subject'
    )

    # Get filters from GET request
    offering_id = request.GET.get('offering')  # can be empty string
    selected_year = request.GET.get('year')
    selected_section = request.GET.get('section')
    selected_status = request.GET.get('status')

    selected_offering = None
    students = StudentProfile.objects.none()

    if offering_id:  # Only filter by offering if not empty
        # Ensure the offering belongs to the logged-in teacher
        selected_offering = get_object_or_404(
            SubjectOffering, id=offering_id, teacher=teacher
        )
        # Restrict to the exact class (course + year + section) for that offering
        students = StudentProfile.objects.filter(
            course=selected_offering.subject.course,
            year=selected_offering.year,
            section=selected_offering.section,
        )
    else:
        # If no offering selected, show only students that are actually
        # enrolled in subjects taught by this teacher (via SubjectOffering)
        # SubjectOffering has related_name='offerings' on Subject
        students = StudentProfile.objects.filter(
            subjects__offerings__teacher=teacher
        ).distinct()

    # Apply additional filters only if a value is selected
    if selected_year:
        students = students.filter(year=selected_year)
    if selected_section:
        students = students.filter(section=selected_section)
    if selected_status:
        students = students.filter(is_regular=selected_status)

    # Dropdown options – restrict to sections/years from this teacher's offerings
    sections = (
        SubjectOffering.objects.filter(teacher=teacher)
        .values_list('section', flat=True)
        .distinct()
    )
    years = (
        SubjectOffering.objects.filter(teacher=teacher)
        .values_list('year', flat=True)
        .distinct()
    )
    statuses = StudentProfile.objects.values_list('is_regular', flat=True).distinct()

    context = {
        'students': students.distinct(),
        'offerings': offerings,
        'selected_offering': offering_id,
        'sections': sections,
        'years': years,
        'selected_section': selected_section,
        'selected_year': selected_year,
        'statuses': statuses,
        'selected_status': selected_status,
    }

    return render(request, 'dashboard/student_list.html', context)
