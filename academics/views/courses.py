from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from ..forms import CourseForm
from ..models import Course, CourseMajor


def _major_names(post_data):
    names = []
    seen = set()
    for raw_name in post_data.getlist('majors'):
        name = raw_name.strip()
        if name.lower().startswith('major in '):
            name = name[9:].strip()
        key = name.casefold()
        if name and key not in seen:
            names.append(name)
            seen.add(key)
    return names


def _sync_majors(course, names):
    existing = {major.name.casefold(): major for major in course.majors.all()}
    retained_ids = []

    for name in names:
        key = name.casefold()
        major = existing.get(key)
        if major:
            if major.name != name:
                major.name = name
                major.save(update_fields=['name'])
        else:
            major = CourseMajor.objects.create(course=course, name=name)
        retained_ids.append(major.id)

    course.majors.exclude(id__in=retained_ids).delete()


@login_required
def manage_courses(request):
    courses = (
        Course.objects.prefetch_related('majors')
        .annotate(
            student_count=Count('studentprofile', distinct=True),
            subject_count=Count('subject', distinct=True),
        )
        .order_by('name')
    )
    return render(request, 'dashboard/manage_courses.html', {
        'courses': courses,
        'course_form': CourseForm(),
        'active': 'courses',
    })


@login_required
@require_POST
def add_course(request):
    form = CourseForm(request.POST)
    if form.is_valid():
        with transaction.atomic():
            course = form.save()
            _sync_majors(course, _major_names(request.POST))
        messages.success(request, f'{course.name} was added successfully.')
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    return redirect('academics:manage_courses')


@login_required
@require_POST
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST, instance=course)
    if form.is_valid():
        with transaction.atomic():
            course = form.save()
            _sync_majors(course, _major_names(request.POST))
        messages.success(request, f'{course.name} was updated successfully.')
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    return redirect('academics:manage_courses')


@login_required
@require_POST
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    name = course.name
    course.delete()
    messages.success(request, f'{name} was deleted successfully.')
    return redirect('academics:manage_courses')


@login_required
@require_GET
def load_majors(request, course_id):
    majors = CourseMajor.objects.filter(course_id=course_id).values('id', 'name')
    return JsonResponse({'majors': list(majors)})
