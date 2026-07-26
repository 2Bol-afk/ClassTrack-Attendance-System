# ClassTrack Attendance System

ClassTrack is a Django web application for managing student attendance across
administrators, teachers, students, and parents.

## Features

- Role-based authentication and dashboards
- Present, absent, and late attendance tracking
- Course, subject, semester, year, and section management
- Teacher-to-subject assignments
- Student and parent attendance reports
- Account export tools

## Quick Start

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

On Windows, activate the environment with:

```powershell
env\Scripts\Activate.ps1
```

Open `http://127.0.0.1:8000/` after the server starts.

## Configuration

Development defaults work without an environment file. Production deployments
should provide the variables documented in [.env.example](.env.example),
especially `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS`.

The application reads these variables directly from the process environment; it
does not automatically load `.env` files.

## Project Structure

```text
ClassTrack-Attendance-System/
|-- manage.py
|-- requirements.txt
|-- classtrack/          # Django settings and root URL configuration
|-- academics/           # Subjects, offerings, and attendance
|-- accounts/            # Users, profiles, and authentication
|-- dashboard/           # Role-specific dashboards
|-- reports/             # Attendance reporting
|-- core/                # Shared templates and static assets
|-- assets/branding/     # Brand analysis and logo concepts
`-- docs/                # Product and workflow documentation
```

Large view modules are organized into feature packages such as
`accounts/views/`, `academics/views/`, and `reports/views/`. Their public
functions are re-exported so the URL configuration remains straightforward.

## Useful Commands

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py populate_attendance --start-date 2025-11-24 --end-date 2025-11-28
python manage.py create_and_assign_teachers --school-year 2024-2025
python manage.py export_accounts
```

## Documentation

- [System documentation](docs/DOCUMENTATION.md)
- [Workflow documentation](docs/WORKFLOW_DOCUMENTATION.txt)
- [Presentation outline](docs/PRESENTATION_OUTLINE.md)
- [Brand analysis](assets/branding/brand-analysis.md)
- [Logo concepts](assets/branding/logo-concepts/)

## Technology

- Python
- Django 5.2
- SQLite for local development
- HTML, CSS, and JavaScript

ClassTrack began as a midterm web development project and is now being
modernized into a maintainable attendance platform.
