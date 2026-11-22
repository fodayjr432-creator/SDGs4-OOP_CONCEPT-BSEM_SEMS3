# Digital Examination Results Management System

A Python project for managing academic programmes, students, examinations, results, and performance reports. It contains a PyQt6 desktop application, a Django REST API, and a separate console workflow.

The intended data path for the desktop application is:

```text
PyQt6 desktop app -> Django REST API -> existing PostgreSQL database
```

The desktop application must not connect directly to PostgreSQL. The console workflow is separate and uses local JSON files; it is not connected to the PostgreSQL database.

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

The backend's academic ORM models map the existing PostgreSQL schema and use unmanaged tables. Do not run schema-changing migrations against the academic database. The backend also uses Django authentication and DRF token authentication for protected API requests.

## Current functionality and limitations

- The desktop supports one-time institution administrator registration and signs in through the backend login endpoint using a DRF token.
- All desktop pages (Dashboard, Students, Programmes, Modules, Examinations, Results, Reports) now communicate with the Django REST API through the `AppState` service layer. Network work runs in a background thread.
- The API prevents deletion when examination results refer to a student.
- The console mode uses JSON data in `frontend/`, not PostgreSQL.
- Public registration is limited to the first institution administrator. Further administrator provisioning and activation changes require an authenticated institution administrator. There are no default or demonstration credentials.
- Automated tests pass for both frontend and backend. The opt-in live PostgreSQL workflow test is documented in `frontend/README.md`.

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or later
- PostgreSQL server and access to the existing project database
- The configured existing PostgreSQL database; do not create or substitute an academic database

The application dependencies are listed separately in [`frontend/requirements.txt`](frontend/requirements.txt) and [`backend/requirements.txt`](backend/requirements.txt).

## Installation

From the repository root, create and activate a virtual environment, then install both dependency sets:

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
2. Set `DJANGO_SECRET_KEY` and the PostgreSQL connection variables to the values provided for your environment: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD`.
3. Keep `backend/.env` private. It is local configuration and must not be committed, pasted into messages, or copied into screenshots.

Do not create a replacement database or change the existing schema to make the application start. If database access or the required tables are unavailable, resolve that with the database administrator before using the application.

The new account migration creates only the institution/profile tables; Django also needs its own authentication and token tables. Before applying migrations to the existing PostgreSQL database, back it up and have the database administrator inspect `python manage.py showmigrations` and `python manage.py migrate --plan`. Apply only the reviewed migrations with approval. No production migration is run by the automated tests.

## Run the application

Open two terminals from the repository root and activate the virtual environment in each.

**Terminal 1 — backend:**

```powershell
cd backend
python manage.py check
python manage.py runserver 127.0.0.1:8000
```

For initial setup, use the login window's **First-time institution setup** route after the reviewed Django migrations have been applied. Enter an institution name, administrator name, username, email, and a strong password. Passwords must be at least 12 characters and include at least one letter, one number, and one special character. Registration closes once an administrator exists. Sign in with the username and password just created; a successful login opens the existing dashboard.

The public health endpoint is [`http://127.0.0.1:8000/api/status/`](http://127.0.1:8000/api/status/). It performs a database connectivity check. A successful health response does not mean that a user is authenticated.

**Terminal 2 — desktop application:**

```powershell
python main.py
```

Sign in using the institution administrator account. Protected API calls use the session token; logging out invalidates the server token and clears the desktop token.

To run the separate console workflow instead:

```powershell
cd frontend
python main.py --console
```

Console records and catalogue files are separate from PostgreSQL and are not automatically imported into the database.

## Tests.

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

The backend test setting uses in-memory SQLite only for isolated tests. It does not replace PostgreSQL and must not be used to run the application. Automated tests must not be pointed at production data.

An opt-in PyQt-to-API live student workflow test is documented in [`frontend/README.md`](frontend/README.md). It requires an authorized account and permission to create and delete its uniquely generated temporary student. Only run it against a database where such a reversible test operation is approved. It prompts for the password without echoing it and cleans up only its own generated record.

## API and data safety

- Initial registration status: `GET /api/auth/registration-status/`.
- First administrator only: `POST /api/auth/register/`, with `institution_name`, `administrator_name`, `username`, `email`, `password`, and `confirm_password`.
- Login: `POST /api/auth/login/`; protected requests send `Authorization: Token <token>`.
- Current account/logout: `GET /api/auth/me/` and `POST /api/auth/logout/`.
- Administrator management: `GET`/`POST /api/auth/admins/` and `PATCH /api/auth/admins/<user_id>/` with `{"is_active": false}` or `{"is_active": true}`. These routes require an active institution administrator token. The last active administrator and the caller cannot be deactivated through the API.
- Student collection: `GET` and `POST /api/students/`.
- Student detail: `GET`, `PUT`, and `DELETE /api/students/<student_id>/`.
- Student search uses the `search` query parameter; programme filtering uses `programme`.
- The displayed student identifier is the admission number. API detail/update paths use the database's integer `student_id`.
- Programmes, modules, academic years, examinations, questions, results, reports, and dashboard endpoints are available under `/api/` and require an active institution administrator token. See [backend/README.md](backend/README.md) for the full endpoint table.
- Do not add demo credentials, seed fake academic records, or use local JSON as a fallback for PostgreSQL data.
- Do not expose passwords or tokens in source control, logs, screenshots, or support requests.
- Use HTTPS outside local development, keep the Django secret key and database credentials private, and never send passwords except over a trusted secure connection. Login and initial registration requests are rate limited.
- For account recovery, a trusted backend operator can run `python manage.py reset_institution_admin_password USERNAME` from `backend/`. The password is prompted without echo and existing tokens are revoked. This command does not activate a disabled account.

## Further reading

- [Frontend documentation](frontend/README.md)
- [Backend setup and API notes](backend/README.md)
- [Architecture](frontend/docs/architecture.md)
- [User guide](frontend/docs/user_guide.md)
- [Developer guide](frontend/docs/developer_guide.md)
