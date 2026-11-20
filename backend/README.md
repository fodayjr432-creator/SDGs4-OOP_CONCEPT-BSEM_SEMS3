# PostgreSQL backend

The Django backend is configured to connect to the existing PostgreSQL
database. Its unmanaged ORM models map the schema inspected in PostgreSQL:
academic years, programmes, modules, students, examinations, questions,
results, and result audit records.

The existing database schema is authoritative. The backend does not create,
seed, migrate, or replace its tables. Do **not** run `manage.py migrate` or
`initialize_db` expecting schema creation; `initialize_db` only verifies the
connection.

## Local configuration

Create `backend/.env` from `.env.example`, then configure the connection values
locally. Do not commit the file or paste its password into chat:

```text
DJANGO_SECRET_KEY=<private random value>
PGHOST=<existing PostgreSQL host>
PGPORT=<existing PostgreSQL port>
PGDATABASE=<exact existing database name>
PGUSER=<database user>
PGPASSWORD=<database password>
```

The local configuration currently targets the existing project database whose
PostgreSQL name contains the literal SQL statement text. This unusual name was
confirmed in the cluster catalog; no database was created or renamed.

Install the backend dependencies from `backend/`:

```powershell
python -m pip install -r requirements.txt
```

## Verify and run

Check Django configuration and verify the PostgreSQL connection without
changing the schema:

```powershell
python manage.py check
python manage.py initialize_db
```

Start the backend bound to the local machine:

```powershell
python manage.py runserver 127.0.0.1:8000
```

`GET http://127.0.0.1:8000/api/status/` runs a real PostgreSQL `SELECT 1` and
reports whether the database is reachable.

## Authentication and API

The login endpoint authenticates an existing Django account and returns a DRF
token. Send it on protected requests as
`Authorization: Token <token>`. The student API supports listing/search,
retrieval, creation, updates, and deletion. Students with examination results
cannot be deleted. The PyQt login and Student Management page use this API;
other GUI modules are not yet claimed as end-to-end verified.

The ORM models use `managed = False` to prevent Django from creating or
altering existing tables. The backend preserves the database's current records
and does not automatically import the frontend's JSON catalogue or create
demonstration accounts. Django authentication/token tables are separate from
the academic schema and are used for application accounts.

Run isolated backend tests without using the configured production database:

```powershell
python manage.py test --settings=config.test_settings
```

`config.test_settings` uses an in-memory SQLite database only for tests. Do not
use those settings to run the application. The root `main.py` starts the PyQt
frontend; start the backend separately from this directory. Production
student-record writes have not been performed as part of verification.
