# User Guide

## Backend status

The desktop application connects to the existing PostgreSQL database through
the Django REST backend. The backend's `/api/status/` endpoint checks the real
database connection.

Sign in with an existing Django application account. There are no default or
demonstration credentials. The Student Management page loads and changes
records through the authenticated API. The frontend does not connect directly
to PostgreSQL.

Do not use the console workflow or its JSON files as a substitute for the
PostgreSQL-backed GUI. Console data is separate and is not imported into the
database.

## Desktop workflow

The desktop includes Dashboard, Students, Programmes, Modules, Examinations,
Results, and Reports pages. Student listing and CRUD are integrated; other
pages have not yet been verified end-to-end against the current backend API.
Use only authorized accounts and follow your institution's data-handling
rules. Student records with examination results cannot be deleted.

## Console workflow

The separate console mode continues to use the frontend's existing JSON-based
workflow. Run it from `frontend/`:

```powershell
python main.py --console
```

Its JSON data is not connected to PostgreSQL. Avoid entering sensitive student
information into the console prototype.
