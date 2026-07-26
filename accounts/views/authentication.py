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
def change_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            user.first_login = False
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")

            # Role-based redirect
            role_redirects = {
                'admin': 'dashboard:admin_dashboard',
                'teacher': 'dashboard:teacher_dashboard',
                'student': 'dashboard:student_dashboard',
                'parent': 'dashboard:dashboard',
            }
            return redirect(role_redirects.get(user.role, 'accounts:login'))
    else:
        form = SetPasswordForm(user=request.user)

    return render(request, 'dashboard/change_password.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST.get('password', '')  # allow blank for first login

        user = authenticate(request, username=username, password=password)



        if user:
            login(request, user)

            if user.first_login:
                return redirect('accounts:change_password')

            # Role-based redirect
            if user.role == 'admin':
                return redirect('dashboard:admin_dashboard')
            elif user.role == 'teacher':
                return redirect('dashboard:teacher_dashboard')
            elif user.role == 'student':
                return redirect('dashboard:student_dashboard')
            elif user.role == 'parent':
                return redirect('dashboard:dashboard')
            else:
                return redirect('accounts:login')

        else:
            messages.error(request, "Invalid Credentials.")

    return render(request, 'dashboard/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')
