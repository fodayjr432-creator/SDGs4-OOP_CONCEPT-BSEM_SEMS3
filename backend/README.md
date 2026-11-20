# Django/PostgreSQL backend

The backend serves the PyQt desktop application through Django REST Framework.
It maps the existing PostgreSQL academic tables with unmanaged ORM models and
uses Django's built-in `User` model plus DRF token authentication for
institution administrator accounts.

## Database and migrations

The existing PostgreSQL database is authoritative. Academic tables,
examination results, and their triggers, procedures, views, and constraints
must not be recreated or modified by this application. The academic ORM
models have `managed = False`.

The accounts migration adds only `accounts_institution` and
`accounts_userprofile`. Django's standard auth, content-types, and DRF token
migrations may also be required. No migration was run against the configured
PostgreSQL database as part of this implementation.

Before any migration against an existing database:

1. Make an approved database backup.
2. From this directory, inspect `python manage.py showmigrations` and
   `python manage.py migrate --plan` using the intended private `.env`.
3. Have the database administrator verify the existing migration history and
   review the planned changes. Apply only the reviewed migrations with
   approval. Do not create a replacement database or mark migrations applied
   without verifying the actual schema.

For isolated automated tests use `config.test_settings`; it uses in-memory
SQLite and does not connect to PostgreSQL:

```powershell
python manage.py test --settings=config.test_settings
```

## Configuration and startup

Create `.env` from `.env.example` and privately configure `DJANGO_SECRET_KEY`
and the existing PostgreSQL connection values (`PGHOST`, `PGPORT`,
`PGDATABASE`, `PGUSER`, `PGPASSWORD`). Do not commit the file or send its
values in logs or support requests.

Install dependencies and check the backend:

```powershell
python -m pip install -r requirements.txt
python manage.py check
```

After migrations are inspected and approved, start the API locally:

```powershell
python manage.py runserver 127.0.0.1:8000
```

The health endpoint is `GET /api/status/`. It checks PostgreSQL connectivity;
it does not indicate whether anyone is logged in.

## First institution administrator

1. Start the backend after the reviewed auth/account migrations are applied.
2. Launch the desktop UI from the repository root with `python main.py`.
3. On the login screen select **First-time institution setup**.
4. Enter the institution name, administrator's full name, username, email,
   password, and password confirmation. Passwords must pass Django's
   configured validators (minimum 12 characters, at least one letter, one
   number and one special character, plus similarity and common-password
   checks).
5. Return to login and sign in using the new username and password. A
   successful administrator login opens the existing dashboard.

The public endpoint closes after one administrator exists. Passwords are
validated by Django, stored only as Django password hashes, and never returned
by the API. Registration is rate limited; deploy through HTTPS outside local
development.

## Authentication and account endpoints

All paths below are under `/api/`.

| Method and path | Access | Purpose |
|---|---|---|
| `GET auth/registration-status/` | Public | Reports whether initial setup is available |
| `POST auth/register/` | Public, one time | Creates the first institution and administrator |
| `POST auth/login/` | Public, rate limited | Accepts `username` and `password`; returns a token for an active institution administrator |
| `GET auth/me/` | Authenticated | Returns the current account and role details |
| `POST auth/logout/` | Authenticated | Deletes the current DRF token |
| `GET auth/admins/` | Institution administrator | Lists safe account details for this institution |
| `POST auth/admins/` | Institution administrator | Provisions an additional institution administrator |
| `PATCH auth/admins/<user_id>/` | Institution administrator | Sets `{"is_active": true}` or `{"is_active": false}` |

Send returned tokens as `Authorization: Token <token>`. Ordinary authenticated
users and inactive users cannot log in as administrators or access academic,
dashboard, reporting, or administrator-management APIs. The API prevents an
administrator from deactivating their own account or the last active
administrator. Account management requests do not return password hashes.

## Provisioning and recovery

An active administrator can provision additional administrators through
`POST /api/auth/admins/`, using the same account fields as registration except
for `institution_name`. Administrator activation/deactivation uses the
corresponding `PATCH` endpoint. There is deliberately no public route for
creating additional administrators.

If an administrator cannot sign in, a trusted operator with approved backend
access can reset the password without placing it in shell history:

```powershell
python manage.py reset_institution_admin_password USERNAME
```

The command prompts for the new password and confirmation without echo,
validates it with Django, and revokes existing tokens. It does not activate a
disabled account. Protect database credentials, the Django secret key, admin
tokens, and access to this command.

## Other API and data safety

The student API supports listing/searching, retrieval, creation, updates, and
deletion. Students referenced by examination results cannot be deleted. The
dashboard and other academic endpoints require the institution administrator
role. Existing academic records are not seeded, imported, or changed by
authentication setup.

### Academic API endpoints

All paths below are under `/api/` and require an active institution
administrator token sent as `Authorization: Token <token>`:

| Method and path | Purpose |
|---|---|
| `GET programmes/` | List programmes (supports `code` query parameter) |
| `GET/POST programmes/` | List or create programmes |
| `GET/PUT/DELETE programmes/<programme_id>/` | Retrieve, update, or delete a programme |
| `GET/POST modules/` | List or create modules |
| `GET/PUT/DELETE modules/<module_id>/` | Retrieve, update, or delete a module |
| `GET academic-years/` | List academic years |
| `GET/POST students/` | List or create students (supports `search` and `programme` query parameters) |
| `GET/PUT/DELETE students/<student_id>/` | Retrieve, update, or delete a student |
| `GET/POST examinations/` | List or create examinations |
| `GET/PUT/DELETE examinations/<examination_id>/` | Retrieve, update, or delete an examination |
| `GET/POST examinations/<examination_id>/questions/` | List or add questions for an examination |
| `GET/PUT/DELETE questions/<question_id>/` | Retrieve, update, or delete a question |
| `GET/POST results/` | List or create results (supports `student` and `examination` query parameters) |
| `GET/PUT/DELETE results/<result_id>/` | Retrieve, update, or delete a result |
| `GET reports/` | Aggregate statistics plus `student_reports` rows for the desktop performance table |
| `GET dashboard/` | Dashboard counts and recent student averages |

Each `student_reports` entry contains the admission-number `student_id`, student
name, programme code, total score, average score, and overall grade. The
aggregate statistics remain at the top level of the response.

Do not use production records in destructive tests. Do not point automated
tests at the configured PostgreSQL database. The root `main.py` starts the
PyQt frontend; start the backend separately from this directory.
