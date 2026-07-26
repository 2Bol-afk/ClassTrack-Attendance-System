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
def manage_teacher(request):
    teachers = TeacherProfile.objects.select_related('user').all()
    # Provide empty forms so the add-teacher modal can render its input fields
    user_form = TeacherUserForm()
    profile_form = TeacherProfileForm()

    return render(request, 'dashboard/manageteacher.html', {
        'teachers': teachers,
        'user_form': user_form,
        'profile_form': profile_form,
        'active': 'teacher',
    })


# -------------------------------
# Add Teacher
# -------------------------------
@login_required
def add_teacher(request):
    try:
        if request.method == "POST":
            user_form = TeacherUserForm(request.POST)
            profile_form = TeacherProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            teacher_first_name = profile_form.cleaned_data['first_name']
            teacher_last_name = profile_form.cleaned_data['last_name']
            teacher_email,teacher_username = generate_unique_email(
                teacher_first_name,teacher_last_name,domain="teacher.isufst.com"
            )

            user = user_form.save(commit=False)
            user.email = teacher_email
            user.username = teacher_username
            user.set_password(get_random_string(8))
            user.first_login = True
            user.role = 'teacher'
            user.save()

            teacher = profile_form.save(commit=False)
            teacher.user = user
            teacher.save()

            messages.success(request, f"Teacher created! Email: {user.email}")
            return redirect('accounts:manage_teacher')

    except IntegrityError:
        user_form.add_error(None,"Email Already exists.")
    except Exception as error:
        profile_form.add_error(None,f'An Unexpected Error occured: {error}')


    else:
        user_form = TeacherUserForm()
        profile_form = TeacherProfileForm()
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'active': 'teacher',
        'teachers' : TeacherProfile.objects.all()
    }

    return render(request, 'dashboard/manageteacher.html', context)


# -------------------------------
# Edit Teacher
# -------------------------------
@login_required
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)

    if request.method == "POST":
        user_form = TeacherUserForm(request.POST, instance=teacher.user)
        profile_form = TeacherProfileForm(request.POST, instance=teacher)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Teacher updated successfully.")
            return redirect('accounts:manage_teacher')
    else:
        user_form = TeacherUserForm(instance=teacher.user)
        profile_form = TeacherProfileForm(instance=teacher)

    return render(request, 'dashboard/manageteacher.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'teacher': teacher,
        'active': 'teacher',
    })


# -------------------------------
# Delete Teacher
# -------------------------------
@login_required
@require_POST
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    teacher.user.delete()  # Delete both user and profile
    teacher.delete()
    messages.success(request, "Teacher deleted successfully.")
    return redirect('accounts:manage_teacher')
