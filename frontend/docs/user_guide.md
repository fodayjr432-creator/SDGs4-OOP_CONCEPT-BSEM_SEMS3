# User Guide

## Backend status

The desktop application is being connected through the Django REST backend to
the existing PostgreSQL database. The backend's `/api/status/` endpoint checks
the real database connection.

The existing PostgreSQL schema does not contain application accounts. Login
and data endpoints are intentionally disabled until secure authentication and
authorization are implemented. The GUI will report that sign-in is unavailable;
there are no default or demonstration credentials.

Do not use the console workflow or its JSON files as a substitute for the
PostgreSQL-backed GUI. Console data is separate and is not imported into the
database.

## Intended desktop workflow

After authenticated API access is implemented, the GUI is intended to provide
Dashboard, Students, Programmes, Modules, Examinations, Results, and Reports.
Until then, do not use those screens to enter or change real academic records.

## Console workflow

The separate console mode continues to use the frontend's existing JSON-based
workflow. Run it from `frontend/`:

```powershell
python main.py --console
```

Its JSON data is not connected to PostgreSQL. Avoid entering sensitive student
information into the console prototype.
