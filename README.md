# Digital Examination Results Management System

A Python project for managing academic programmes, students, examinations,
results, and performance reports. It contains a PyQt6 desktop application, a
Django REST API, and a separate console workflow.

The intended data path for the desktop application is:

```text
PyQt6 desktop app -> Django REST API -> existing PostgreSQL database
```

The desktop application must not connect directly to PostgreSQL. The console
workflow is separate and uses local JSON files; it is not connected to the
PostgreSQL database.

## What is in this repository?

| Folder/file | Purpose |
|---|---|
| `frontend/` | Desktop UI, Python domain classes, API client, console workflow, and frontend tests |
| `frontend/gui/` | PyQt6 login, main window, pages, components, and background API worker |
| `backend/` | Django REST API, PostgreSQL configuration, API serializers/views, and backend tests |
| `backend/apps/academics/` | Existing academic year, programme, and module table mappings |
| `backend/apps/students/` | Student table mapping and API serializer |
| `backend/apps/examinations/` | Examination and question table mappings |
| `backend/apps/results/` | Examination result mappings |
| `frontend/docs/` | Architecture, developer, and user guides |
| `main.py` | Root launcher for the desktop application |

The backend's academic ORM models map the existing PostgreSQL schema and use
unmanaged tables. Do not run schema-changing migrations against the academic
database. The backend also uses Django authentication and DRF token
authentication for protected API requests.

## Current functionality and limitations

- The desktop login calls the backend login endpoint and uses its DRF token for
  authenticated API requests.
- The Student Management page supports listing, searching, programme
  filtering, viewing a selected student's current details, creating, editing,
  and deleting students through the API. Network work runs in a background
  thread. The API prevents deletion when examination results refer to a
  student.
- Dashboard, programme, module, examination, result, and report screens exist;
  they have not all been verified end-to-end against PostgreSQL.
- The console mode uses JSON data in `frontend/`, not PostgreSQL.
- A production-data student create/edit/delete workflow has not been run as
  part of the automated verification. Do not treat isolated test results as
  proof of production persistence.
- Login requires an existing backend account. There are no default or
  demonstration credentials. Account provisioning must be handled through an
  authorized, approved process; do not use the unavailable
  `create_account`/`create_admin` commands.

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or later
- PostgreSQL server and access to the existing project database
- Existing authorized backend account for signing in to the desktop app

The application dependencies are listed separately in
[`frontend/requirements.txt`](frontend/requirements.txt) and
[`backend/requirements.txt`](backend/requirements.txt).

## Installation

From the repository root, create and activate a virtual environment, then
install both dependency sets:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r frontend\requirements.txt
python -m pip install -r backend\requirements.txt
```

On macOS or Linux, activate the environment with:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r frontend/requirements.txt
python -m pip install -r backend/requirements.txt
```

## Configure the backend

1. Make a private local copy of `backend/.env.example` named `backend/.env`.
2. Set `DJANGO_SECRET_KEY` and the PostgreSQL connection variables to the
   values provided for your environment:
   `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD`.
3. Keep `backend/.env` private. It is local configuration and must not be
   committed, pasted into messages, or copied into screenshots.

Do not create a replacement database or change the existing schema to make
the application start. If database access or the required tables are
unavailable, resolve that with the database administrator before using the
application.

## Run the application

Open two terminals from the repository root and activate the virtual
environment in each.

**Terminal 1 — backend:**

```powershell
cd backend
python manage.py check
python manage.py runserver 127.0.0.1:8000
```

The public health endpoint is
[`http://127.0.0.1:8000/api/status/`](http://127.0.0.1:8000/api/status/).
It performs a database connectivity check. A successful health response does
not mean that a user is authenticated.

**Terminal 2 — desktop application:**

```powershell
python main.py
```

Sign in using an existing authorized backend account. Protected API calls use
the session token; logging out clears the desktop token.

To run the separate console workflow instead:

```powershell
cd frontend
python main.py --console
```

Console records and catalogue files are separate from PostgreSQL and are not
automatically imported into the database.

## Tests

Run frontend tests from `frontend/`:

```powershell
cd frontend
python -m unittest discover -s tests -v
```

Run backend tests with the test-only in-memory database:

```powershell
cd backend
python manage.py test --settings=config.test_settings
```

The backend test setting uses in-memory SQLite only for isolated tests. It
does not replace PostgreSQL and must not be used to run the application.
Automated tests must not be pointed at production data.

An opt-in PyQt-to-API live student workflow test is documented in
[`frontend/README.md`](frontend/README.md). It requires an authorized account
and permission to create and delete its uniquely generated temporary student.
Only run it against a database where such a reversible test operation is
approved. It prompts for the password without echoing it and cleans up only
its own generated record.

## API and data safety

- Login: `POST /api/auth/login/`; protected requests send
  `Authorization: Token <token>`.
- Student collection: `GET` and `POST /api/students/`.
- Student detail: `GET`, `PUT`, and `DELETE /api/students/<student_id>/`.
- Student search uses the `search` query parameter; programme filtering uses
  `programme`.
- The displayed student identifier is the admission number. API detail/update
  paths use the database's integer `student_id`.
- Do not add demo credentials, seed fake academic records, or use local JSON
  as a fallback for PostgreSQL data.
- Do not expose passwords or tokens in source control, logs, screenshots, or
  support requests.

## Further reading

- [Frontend documentation](frontend/README.md)
- [Backend setup and API notes](backend/README.md)
- [Architecture](frontend/docs/architecture.md)
- [User guide](frontend/docs/user_guide.md)
- [Developer guide](frontend/docs/developer_guide.md)
