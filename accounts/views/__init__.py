from .helpers import generate_unique_email
from .teachers import manage_teacher, add_teacher, edit_teacher, delete_teacher
from .students import manage_student, add_student, edit_student, delete_student, load_subjects
from .parents import manage_parents, add_parent, edit_parent, delete_parent
from .authentication import change_password, custom_login, logout_view
from .administration import accounts_dashboard, export_accounts_view

__all__ = [
    'generate_unique_email',
    'manage_teacher',
    'add_teacher',
    'edit_teacher',
    'delete_teacher',
    'manage_student',
    'add_student',
    'edit_student',
    'delete_student',
    'load_subjects',
    'manage_parents',
    'add_parent',
    'edit_parent',
    'delete_parent',
    'change_password',
    'custom_login',
    'logout_view',
    'accounts_dashboard',
    'export_accounts_view',
]
