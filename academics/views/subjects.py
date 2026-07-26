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
def manage_subject(request):
    subjects = Subject.objects.all()
    courses = Course.objects.all()
    add_form = SubjectForm()
    return render(request, 'dashboard/managesubjects.html', {
        'subjects': subjects,
        'add_form': add_form,
        'courses': courses,
        'active': 'subjects',
    })

@login_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject {subject.subject_code} created successfully.')
    return redirect('academics:manage_subjects')

@login_required
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subject {subject.subject_code} updated successfully.')
    return redirect('academics:manage_subjects')

@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, f'Subject {subject.subject_code} deleted successfully.')
    return redirect('academics:manage_subjects')

# -------------------------------
# Assign Teacher (Page-based)
# -------------------------------
