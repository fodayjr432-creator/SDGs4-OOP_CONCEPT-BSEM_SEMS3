# Digital Examination Results Management System

A Python OOP learning project for managing academic programmes, students,
examinations, results, and performance reports. It includes a PyQt6 desktop
application and a separate console workflow. It is an academic prototype, not
an official examination platform or a production student-records system.

The project uses the Ministry of Basic and Senior Secondary Education (MBSSE)
in Sierra Leone as an educational context. It is not affiliated with or
endorsed by MBSSE. The project relates to SDG 4 (Quality Education) but does
not claim official SDG or Digital Public Good status.

## Features

- PyQt6 dashboard with student, programme, module, examination, result, and
  report pages.
- A Django REST backend under `backend/` configured for the existing
  PostgreSQL schema, with DRF token authentication and protected data APIs.
- The desktop login uses the backend token API. Student listing, registration,
  updates, deletion, and search use the backend; other GUI modules still need
  end-to-end verification.
- The separate console workflow retains JSON persistence for its records and
  catalogue data.
- CSV export for student performance reports.
- Console workflow for entering examination results and deleting a student
  record.
- OOP domain models for students, programmes, modules, examinations,
  questions, and exam results.
- Score validation and letter-grade calculation.

## Technologies

- Python 3
- PyQt6
- Django, Django REST Framework, PostgreSQL, and Django ORM
- JSON and the Python standard library
- `unittest` for tests

## Object-oriented concepts and grading

The project demonstrates classes, object construction, validation,
encapsulation, and object relationships:

- `Student` stores a student ID, name, age, and optional programme.
- `Programme` owns `Module` objects and can filter active modules by level or
  semester.
- `Examination` contains `Question` objects. Objective questions can be
  automatically checked; short-answer questions require manual marking.
- `ExamResult` associates a student and subject with a validated score and
  calculated grade.
- `RecordStore` reads and writes student/result records as JSON.

Scores from 70 to 100 receive A; 60 to below 70 receive B; 50 to below 60
receive C; 40 to below 50 receive D; scores below 40 receive F. Scores must be
finite and within 0–100.

## Example console result

```text
Student ID: ST001
Student Name: Mohamed
Age: 20

Subject: Mathematics
Score: 72.0
Grade: A

Subject: Physics
Score: 65.0
Grade: B

Total Score: 137.0
Average Score: 68.50
Overall Grade: B
```

The example is illustrative. Use fictional student details only.

## Project structure

```text
.
├── frontend/                   # PyQt6 desktop application and its files
│   ├── main.py                 # Console entry point and app dispatcher
│   ├── student.py             # Student model
│   ├── programme.py            # Programme and Module models
│   ├── examination.py          # Examination and Question models
│   ├── exam_result.py          # ExamResult validation and grading
│   ├── storage.py              # JSON record store
│   ├── programmes.json         # Existing programme catalogue
│   ├── requirements.txt        # Frontend dependencies
│   ├── docs/                   # Frontend documentation
│   ├── screenshots/            # Screenshot assets and notes
│   ├── tests/                  # Frontend tests
│   └── gui/                    # PyQt6 interface
├── backend/                    # Independent Django REST API scaffold
├── main.py                     # Root compatibility launcher
```

The console workflow's JSON files are stored in `frontend/`. The repository
also contains `frontend/instance/exam_portal.db`, a legacy SQLite file that is
not the active backend database. The Django backend maps the existing
PostgreSQL tables without creating or migrating them.

## Installation

Use Python 3 and install the desktop dependency from the `frontend/` directory:

```powershell
cd frontend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the application

Start the PyQt6 desktop application from the project root:

```powershell
python main.py
```

To run the console workflow, run from `frontend/`:

```powershell
python main.py --console
```

## Run the backend

Configure the existing PostgreSQL connection in the ignored `backend/.env`
file, then follow [backend/README.md](../backend/README.md). Start the server
from `backend/`:

```powershell
python manage.py runserver 127.0.0.1:8000
```

`http://127.0.0.1:8000/api/status/` verifies the PostgreSQL connection with a
real `SELECT 1`. The login endpoint issues a DRF token for an existing Django
account. Protected endpoints require `Authorization: Token <token>`. The
Student Management page uses those endpoints; do not treat the separate
console/JSON workflow as PostgreSQL data.

## Tests

Run the frontend tests from `frontend/`:

```powershell
python -m unittest discover -s tests -v
```

The GUI tests use PyQt6 and set Qt to the offscreen platform when needed.
Run backend tests from `backend/` with
`python manage.py test --settings=config.test_settings`; those tests use an
isolated in-memory SQLite database and do not write to the configured
PostgreSQL database.

An opt-in live GUI/API student workflow test is available as
`tests.test_live_student_workflow`. Run it from `frontend/` only against the
intended PostgreSQL-backed API, with an existing authorized account:

```powershell
$env:EXAM_RUN_LIVE_STUDENT_TESTS = "YES"
$env:EXAM_LIVE_TEST_USERNAME = "your-existing-account"
python -m unittest tests.test_live_student_workflow -v
Remove-Item Env:EXAM_RUN_LIVE_STUDENT_TESTS
Remove-Item Env:EXAM_LIVE_TEST_USERNAME
```

The test prompts for the password without echoing it, creates a uniquely named
temporary student, exercises the PyQt page's create/search/edit/reload/delete
flow, and removes only that exact generated student during cleanup. Do not run
it unless you have permission to create and delete that temporary record in
the configured database.

## Data storage

- The separate console workflow stores its student and result records in
  `records.json` and its catalogues in JSON files.
- The PyQt Student Management page reads and writes student records through the
  authenticated API and existing PostgreSQL tables.
- These paths are stored in `frontend/` when launched with the root
  compatibility launcher.
- The SQLite file in `instance/` is not read or written by current application
  code.

Keep backups of any records you care about. Avoid entering real student data in
this learning prototype. See the [data and architecture notes](docs/architecture.md)
for the current persistence flow and limitations.

  ## Educational context and privacy

  This project is a learning prototype in an education-sector context. It is not
  an official national examination system and is not certified as a Digital
  Public Good. The configured PostgreSQL database contains real records; use
  existing authorized accounts only and do not use the console workflow for
  PostgreSQL records.

  ## Documentation

- [Architecture](docs/architecture.md)
- [User guide](docs/user_guide.md)
- [Developer guide](docs/developer_guide.md)
- [Screenshot documentation](screenshots/screenshot_documentation.md)

## Current limitations and future work

- Backend token authentication is implemented using Django accounts. The API
  currently applies authenticated-user access; a finer role/permission policy
  has not been specified or verified.
- JSON writes are direct file writes rather than atomic/transactional updates.
- Persistence paths depend on the current working directory.
- Only login and Student Management GUI flows have been integrated/tested in
  this phase. Other GUI modules are not claimed as end-to-end verified.
- The console workflow remains separate and uses JSON files; those files are
  not imported into PostgreSQL.
- Automated student CRUD tests use isolated test data. No production student
  records were created or modified during verification, and persistence across
  a production application restart has not been exercised.
- Future improvements may include safer JSON writes, clearer persistence error
  reporting, additional tests, and a production-ready identity solution. Any
  such work should preserve existing records and be planned separately.
