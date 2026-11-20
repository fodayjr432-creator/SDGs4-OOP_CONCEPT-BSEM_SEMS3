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
  PostgreSQL schema.
- The backend exposes a database health check; record and login endpoints
  remain disabled until authentication is implemented.
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
real `SELECT 1`. Authentication was deferred because the existing schema has
no application account table. Login and academic-data endpoints return HTTP
503; the desktop GUI cannot yet read or modify PostgreSQL records.

## Tests

Run the frontend tests from `frontend/`:

```powershell
python -m unittest discover -v
```

The GUI tests use PyQt6 and set Qt to the offscreen platform when needed.

## Data storage

- Student and result records are stored in `records.json` by `RecordStore`.
- Programme definitions are loaded from and saved to `programmes.json`.
- Examination definitions are loaded from and saved to `examinations.json`.
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
  Public Good. The configured PostgreSQL database contains real records; the
  GUI data endpoints remain closed while authentication is deferred.

  ## Documentation

- [Architecture](docs/architecture.md)
- [User guide](docs/user_guide.md)
- [Developer guide](docs/developer_guide.md)
- [Screenshot documentation](screenshots/screenshot_documentation.md)

## Current limitations and future work

- Backend authentication and authorization are not implemented because no
  account table exists in the inspected PostgreSQL schema.
- JSON writes are direct file writes rather than atomic/transactional updates.
- Persistence paths depend on the current working directory.
- The GUI's PostgreSQL data operations remain disabled until authenticated API
  services are implemented.
- The console workflow remains separate and uses JSON files; those files are
  not imported into PostgreSQL.
- Test coverage currently focuses on login flow and score validation; broader
  persistence and page-level tests would be useful.
- Future improvements may include safer JSON writes, clearer persistence error
  reporting, additional tests, and a production-ready identity solution. Any
  such work should preserve existing records and be planned separately.
