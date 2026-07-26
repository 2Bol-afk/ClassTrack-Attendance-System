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
def manage_parents(request):
    parents = ParentProfile.objects.all()
    return render(request,'dashboard/manage_parents.html',{
        'parents': parents,
        'user_form': parentUserForm(),
        'parent_form': parentProfileForm(),
    })
@login_required
def add_parent(request):
    try:
        if request.method == 'POST':
            user_form = parentUserForm(request.POST)
            parent_form = parentProfileForm(request.POST)

        if user_form.is_valid() and parent_form.is_valid():

            parent_first_name = parent_form.cleaned_data['first_name']
            parent_last_name = parent_form.cleaned_data['last_name']
            parent_email,parent_username =  generate_unique_email(
                parent_first_name,parent_last_name,domain="parent.isufst.com"
            )
            user = user_form.save(commit=False)
            user.email = parent_email
            user.username = parent_username
            user.set_password(get_random_string(8))
            user.role = 'parent'
            user.first_login = True
            user.save()

            parent = parent_form.save(commit=False)
            parent.user = user
            parent.save()

            return redirect('accounts:manage_parent')
    except IntegrityError:
        user_form.add_error(None,"Email Already exists.")
    except Exception as error:
        parent_form.add_error(None,f"An unexpected Errror occured: {error}")

    else:
        user_form = parentUserForm()
        parent_form = parentProfileForm()
    return render(request,'dashboard/manage_parents.html',{
        'user_form':user_form,
        'parent_form':parent_form,
        'parents': ParentProfile.objects.all()
    })
@login_required
def edit_parent(request,parent_id):
    parent = get_object_or_404(ParentProfile,id=parent_id)

    if request.method == "POST":
        parent_form = parentProfileForm(request.POST, instance=parent)

        if parent_form.is_valid():
            parent_form.save()
            messages.success(request,"Parent Updated successfully")
            return redirect('accounts:manage_parent')
    else:
        parent_form = parentProfileForm(instance=parent)

    return render (request, 'dashboard/manage_parents.html',{
        'parent':parent,
        'parent_form': parent_form
    })
@login_required
def delete_parent(request, parent_id):
    parent = get_object_or_404(ParentProfile, id=parent_id)
    if request.method == "POST":
        parent.user.delete()
        parent.delete()

        messages.success(request, "Parent successfully deleted.")
    return redirect('accounts:manage_parent')  # redirect to parent list
