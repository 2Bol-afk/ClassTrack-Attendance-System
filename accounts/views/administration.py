from django.shortcuts import render, redirect, get_object_or_404
from ..models import TeacherProfile,StudentProfile,CustomUser,ParentProfile
from ..forms import TeacherProfileForm, TeacherUserForm,StudentUserForm,StudentProfileForm,parentProfileForm,parentUserForm
from django.contrib.auth import get_user_model,update_session_auth_hash,authenticate,login,logout
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_GET
from academics.models import Semester, Subject, SubjectOffering,Course
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from accounts.constants import YEAR_LEVEL_CHOICES, SECTION_CHOICES
from django.core.management import call_command
import os



User = get_user_model()


@login_required
def accounts_dashboard(request):
    # --- Filters ---
    selected_role = request.GET.get('role')
    selected_year = request.GET.get('year')
    selected_section = request.GET.get('section')
    selected_course = request.GET.get('course')

    # --- Students ---
    student_groups = {}
    if selected_role in ['', 'student']:
        students = StudentProfile.objects.all()
        if selected_year:
            students = students.filter(year=selected_year)
        if selected_section:
            students = students.filter(section=selected_section)
        if selected_course:
            students = students.filter(course__id=selected_course)

        for s in students:
            key = f"{s.year} - {s.section}"
            if key not in student_groups:
                student_groups[key] = []
            student_groups[key].append({
                "first_name": s.first_name,
                "last_name": s.last_name,
                "email": s.user.email,
                "password": s.user.plain_password if hasattr(s.user, 'plain_password') else "N/A",
                "course": s.course.name if s.course else "N/A",
            })

    # --- Parents filtered by their children ---
    parent_groups = []
    if selected_role in ['', 'parent']:
        parents = ParentProfile.objects.all()
        if selected_year or selected_section or selected_course:
            # filter parents whose children match criteria
            filtered_parents = []
            for p in parents:
                children = p.students.all()
                if selected_year:
                    children = children.filter(year=selected_year)
                if selected_section:
                    children = children.filter(section=selected_section)
                if selected_course:
                    children = children.filter(course__id=selected_course)
                if children.exists():
                    filtered_parents.append((p, children))
            parents = [p for p, _ in filtered_parents]

        for p in parents:
            children = ", ".join([f"{c.first_name} {c.last_name}" for c in p.students.all()])
            parent_groups.append({
                "first_name": p.first_name,
                "last_name": p.last_name,
                "children": children,
                "email": p.user.email,
                "password": p.user.plain_password if hasattr(p.user, 'plain_password') else "N/A",
            })

    # --- Teachers ---
    # --- Teachers ---
    teacher_records = []
    if selected_role in ['', 'teacher']:
        teachers = TeacherProfile.objects.all()

        # Optional: filter by year/course if selected
        if selected_year:
            teachers = teachers.filter(subjects__year=selected_year).distinct()
        if selected_course:
            teachers = teachers.filter(subjects__subject__course__id=selected_course).distinct()

        for t in teachers:
            # attach all subject offerings for template
            t.subject_offerings = t.subjects.all()
            teacher_records.append(t)


    # --- Courses for dropdown ---
    courses = Course.objects.all()

    context = {
        "student_groups": student_groups,
        "parent_groups": parent_groups,
        "teacher_records": teacher_records,
        "courses": courses,
        "selected_year": selected_year,
        "selected_section": selected_section,
        "selected_course": selected_course,
        "selected_role": selected_role,
        "year_levels": YEAR_LEVEL_CHOICES,
        "sections": SECTION_CHOICES,
    }

    return render(request, "dashboard/dashboard_accounts.html", context)

@login_required
def export_accounts_view(request):
    """
    Runs the export_accounts management command and returns the Excel file as download.
    """
    output_file = "school_accounts.xlsx"

    # Run the management command
    call_command("export_accounts")

    # Serve the file as download
    if os.path.exists(output_file):
        with open(output_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={output_file}'
            return response
    else:
        return HttpResponse("Export failed, file not found.", status=404)
