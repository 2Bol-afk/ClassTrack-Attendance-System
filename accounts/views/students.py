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

from .helpers import generate_unique_email


@login_required
def manage_student(request):
    students = StudentProfile.objects.select_related('course').all()

    # Attach subjects to each student
    for student in students:
        offerings = SubjectOffering.objects.filter(
            year=student.year,
            subject__course=student.course
        )
        student.subject_list = [o.subject for o in offerings]

    return render(request, 'dashboard/managestudents.html', {
        'students': students
    })

@login_required

def add_student(request):
    semester = request.POST.get('semester', '1st')
    course = request.POST.get('course', None)
    year = request.POST.get('year', None)

    if request.method == 'POST':
        selected_parent_id = request.POST.get('parent_select', '').strip()
        create_new_parent = not selected_parent_id

        user_form = StudentUserForm(request.POST)
        student_form = StudentProfileForm(request.POST, semester=semester, course=course)

        if create_new_parent:
            # ✅ ADD PREFIX to avoid field name collision
            parent_user_form = parentUserForm(request.POST, prefix='parent')
            parent_profile_form = parentProfileForm(request.POST, prefix='parent')
            valid_parent_forms = parent_user_form.is_valid() and parent_profile_form.is_valid()
        else:
            parent_user_form = parentUserForm(prefix='parent')
            parent_profile_form = parentProfileForm(prefix='parent')
            valid_parent_forms = True

        if user_form.is_valid() and student_form.is_valid() and valid_parent_forms:
            try:
                # Parent handling
                if create_new_parent:
                    parent_first = parent_profile_form.cleaned_data['first_name']
                    parent_last = parent_profile_form.cleaned_data['last_name']
                    parent_email, parent_username = generate_unique_email(
                        parent_first, parent_last, domain="parent.isufst.com"
                    )

                    parent_user = parent_user_form.save(commit=False)
                    parent_user.email = parent_email
                    parent_user.username = parent_username
                    parent_user.set_password(get_random_string(8))
                    parent_user.role = 'parent'
                    parent_user.first_login = True
                    parent_user.save()

                    parent_profile = parent_profile_form.save(commit=False)
                    parent_profile.user = parent_user
                    parent_profile.save()
                else:
                    parent_profile = ParentProfile.objects.get(id=int(selected_parent_id))

                # Student handling
                student_first = student_form.cleaned_data['first_name']
                student_last = student_form.cleaned_data['last_name']
                student_email, student_username = generate_unique_email(
                    student_first, student_last, domain="student.isufst.com"
                )

                student_user = user_form.save(commit=False)
                student_user.email = student_email
                student_user.username = student_username
                student_user.set_password(get_random_string(8))
                student_user.role = 'student'
                student_user.first_login = True
                student_user.save()

                student_profile = student_form.save(commit=False)
                student_profile.user = student_user
                student_profile.save()

                # Link student to parent
                student_profile.parents.add(parent_profile)

                # Assign subjects
                subject_ids = [int(i) for i in request.POST.getlist('subjects') if i]
                if subject_ids:
                    student_profile.subjects.set(subject_ids)

                messages.success(request, f"Student {student_first} {student_last} added successfully!")
                return redirect('accounts:manage_student')

            except IntegrityError as e:
                user_form.add_error(None, "Email or Student ID already exists.")
                if create_new_parent:
                    parent_user_form.add_error(None, "Parent email already exists.")
            except Exception as error:
                student_form.add_error(None, f"An unexpected error occurred: {str(error)}")

    else:
        user_form = StudentUserForm()
        student_form = StudentProfileForm(semester=semester, course=course)
        # ✅ ADD PREFIX for GET request too
        parent_user_form = parentUserForm(prefix='parent')
        parent_profile_form = parentProfileForm(prefix='parent')

    subjects = Subject.objects.filter(semester_number=semester)
    if course:
        subjects = subjects.filter(course_id=course)
    if year:
        subject_ids = SubjectOffering.objects.filter(year=year).values_list('subject_id', flat=True)
        subjects = subjects.filter(id__in=subject_ids)

    parents = ParentProfile.objects.all().order_by('first_name', 'last_name')

    forms_list = [user_form, student_form, parent_user_form, parent_profile_form]

    return render(request, 'dashboard/add_student.html', {
        'user_form': user_form,
        'student_form': student_form,
        'parent_user_form': parent_user_form,
        'parent_profile_form': parent_profile_form,
        'semester': semester,
        'subjects': subjects,
        'forms_list': forms_list,
        'parents': parents,
    })
@login_required
def edit_student(request, student_id):
    student_profile = get_object_or_404(StudentProfile, pk=student_id)

    # Get current semester from student profile or default to '1st'
    semester = request.POST.get('semester', student_profile.semester if hasattr(student_profile, 'semester') else '1st')

    if request.method == 'POST':
        selected_parent_id = request.POST.get('parent_select', '').strip()
        parent_action = request.POST.get('parent_action', 'keep')
        create_new_parent = parent_action == 'add' and not selected_parent_id

        student_form = StudentProfileForm(request.POST, instance=student_profile, semester=semester, course=student_profile.course.id if student_profile.course else None)

        if create_new_parent:
            # ✅ ADD PREFIX to avoid field name collision
            parent_user_form = parentUserForm(request.POST, prefix='parent')
            parent_profile_form = parentProfileForm(request.POST, prefix='parent')
            valid_parent_forms = parent_user_form.is_valid() and parent_profile_form.is_valid()
        else:
            parent_user_form = parentUserForm(prefix='parent')
            parent_profile_form = parentProfileForm(prefix='parent')
            valid_parent_forms = True

        if student_form.is_valid() and valid_parent_forms:
            try:
                # Save student
                student = student_form.save()

                # Handle subjects
                subject_ids = [int(i) for i in request.POST.getlist('subjects') if i]
                if subject_ids:
                    student.subjects.set(subject_ids)

                # Handle parent logic
                if parent_action == 'change' and selected_parent_id:
                    # Change to existing parent
                    parent = ParentProfile.objects.get(pk=int(selected_parent_id))
                    student.parents.set([parent])

                elif parent_action == 'add' and create_new_parent:
                    # Create new parent
                    parent_first = parent_profile_form.cleaned_data['first_name']
                    parent_last = parent_profile_form.cleaned_data['last_name']
                    parent_email, parent_username = generate_unique_email(
                        parent_first, parent_last, domain="parent.isufst.com"
                    )

                    parent_user = parent_user_form.save(commit=False)
                    parent_user.email = parent_email
                    parent_user.username = parent_username
                    parent_user.set_password(get_random_string(8))
                    parent_user.role = 'parent'
                    parent_user.first_login = True
                    parent_user.save()

                    parent_profile = parent_profile_form.save(commit=False)
                    parent_profile.user = parent_user
                    parent_profile.save()

                    # Add new parent to student
                    student.parents.add(parent_profile)

                # If parent_action == 'keep', do nothing with parents

                messages.success(request, f'{student.full_name} updated successfully.')
                return redirect('accounts:manage_student')

            except IntegrityError as e:
                student_form.add_error(None, "Student ID or email already exists.")
                if create_new_parent:
                    parent_user_form.add_error(None, "Parent email already exists.")
            except Exception as error:
                student_form.add_error(None, f"An unexpected error occurred: {str(error)}")
    else:
        student_form = StudentProfileForm(instance=student_profile, semester=semester, course=student_profile.course.id if student_profile.course else None)
        # ✅ ADD PREFIX for GET request too
        parent_user_form = parentUserForm(prefix='parent')
        parent_profile_form = parentProfileForm(prefix='parent')

    # Get subjects filtered by student's course, year, and semester
    subjects = Subject.objects.filter(
        course=student_profile.course,
        semester_number=semester
    )

    # Filter by year using SubjectOffering
    subject_ids = SubjectOffering.objects.filter(year=student_profile.year).values_list('subject_id', flat=True)
    subjects = subjects.filter(id__in=subject_ids)

    enrolled_subject_ids = student_profile.subjects.values_list('id', flat=True)

    # Get current parents and available parents
    current_parents = student_profile.parents.all()
    parents = ParentProfile.objects.exclude(id__in=current_parents).order_by('first_name', 'last_name')

    forms_list = [student_form, parent_user_form, parent_profile_form]

    context = {
        'student_profile': student_profile,
        'student_form': student_form,
        'parent_user_form': parent_user_form,
        'parent_profile_form': parent_profile_form,
        'current_parents': current_parents,
        'parents': parents,
        'subjects': subjects,
        'enrolled_subject_ids': enrolled_subject_ids,
        'semester': semester,
        'forms_list': forms_list,
    }
    return render(request, 'dashboard/edit_student.html', context)



@login_required
def delete_student(request, student_id):
    student = get_object_or_404(StudentProfile, student_ID=student_id.strip())
    student_name = f"{student.first_name} {student.last_name}"
    student.delete()
    messages.success(request, f"Student {student_name} has been successfully deleted.")
    return redirect('accounts:manage_student')
@login_required
def load_subjects(request):
    semester = request.GET.get('semester')
    course_id = request.GET.get('course')
    year = request.GET.get('year')

    subjects = Subject.objects.all()

    if semester:
        subjects = subjects.filter(semester_number=semester)
    if course_id:
        subjects = subjects.filter(course_id=course_id)
    if year:
        # Only include subjects assigned to this year in SubjectOffering
        subject_ids = SubjectOffering.objects.filter(year=year).values_list('subject_id', flat=True)
        subjects = subjects.filter(id__in=subject_ids)

    data = [{'id': s.id, 'subject_code': s.subject_code, 'name': s.name} for s in subjects]
    return JsonResponse({'subjects': data})
