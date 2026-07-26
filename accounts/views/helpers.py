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


def generate_unique_email(first_name, last_name, domain="css.com"):
    # Base parts
    base = f"{slugify(first_name)}.{slugify(last_name)}"
    domain = domain.lower()

    # ---- UNIQUE EMAIL ----
    email = f"{base}@{domain}"
    counter = 1
    while CustomUser.objects.filter(email=email).exists():
        email = f"{base}{counter}@{domain}"
        counter += 1   # <-- FIXED (you wrote =+1 which is wrong)

    # ---- UNIQUE USERNAME ----
    username = base
    counter = 1
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base}{counter}"
        counter += 1

    return email, username




# -------------------------------
# Teacher List / Dashboard
# -------------------------------
