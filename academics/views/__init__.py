from .subjects import manage_subject, add_subject, edit_subject, delete_subject
from .offerings import assign_teacher, add_assignment_page, edit_assignment_page, delete_assignment, subject_assign
from .attendance import mark_attendance, student_list
from .courses import add_course, delete_course, edit_course, load_majors, manage_courses

__all__ = [
    'manage_subject',
    'add_subject',
    'edit_subject',
    'delete_subject',
    'assign_teacher',
    'add_assignment_page',
    'edit_assignment_page',
    'delete_assignment',
    'subject_assign',
    'mark_attendance',
    'student_list',
    'manage_courses',
    'add_course',
    'edit_course',
    'delete_course',
    'load_majors',
]
