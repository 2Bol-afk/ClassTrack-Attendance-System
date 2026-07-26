from .administration import admin_dashboard
from .teachers import teacher_home
from .students import student_dashboard, student_subjects, student_attendance_overview
from .parents import children_list, parent_dashboard, attendance_detail_per_subject, parent_student_attendance_overview

__all__ = [
    'admin_dashboard',
    'teacher_home',
    'student_dashboard',
    'student_subjects',
    'student_attendance_overview',
    'children_list',
    'parent_dashboard',
    'attendance_detail_per_subject',
    'parent_student_attendance_overview',
]
