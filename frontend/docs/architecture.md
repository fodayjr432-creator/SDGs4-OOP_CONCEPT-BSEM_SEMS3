# Architecture

## Intended data flow

The application is being integrated using:

```text
PyQt6 frontend -> Django REST API -> existing PostgreSQL database
```

The frontend must call the API; it must never connect to PostgreSQL directly.
The backend owns validation, authorization, business rules, and persistence.

## Current state

- `frontend/gui/` contains the PyQt6 interface. The GUI's `ApiClient` calls the
  local Django API.
- `backend/config/settings.py` loads PostgreSQL credentials from the ignored
  `backend/.env`.
- Django unmanaged models map to the existing `academic_years`, `programmes`,
  `modules`, `programme_modules`, `students`, `examinations`, `questions`,
  `exam_results`, and `result_audit` tables. `managed = False` prevents Django
  migrations from creating or changing those tables.
- `GET /api/status/` runs a real PostgreSQL `SELECT 1`.
- The existing PostgreSQL schema has no application account/user table.
  Authentication was deferred, so login and academic-data API endpoints return
  HTTP 503. They do not fall back to demo credentials, JSON, or SQLite.
- The standalone console workflow continues to use its existing JSON files.
  Those files are not the PostgreSQL database and are not imported automatically.

## Database schema relationships

- Students reference programmes.
- Programmes and modules are linked through `programme_modules`.
- Examinations reference modules and academic years.
- Questions belong to examinations.
- Exam results reference students and examinations.
- `result_audit` stores result change audit entries.

The PostgreSQL schema is authoritative. Do not run migrations or schema
initialization against it. Before implementing CRUD, add and verify the
authenticated service/repository layer against these existing tables, then
test writes using explicit, reversible test operations.

## Grading rules

The existing frontend `ExamResult` model accepts finite numeric scores from
0 through 100 and maps them to A (70+), B (60+), C (50+), D (40+), and F
(below 40). Backend result validation must preserve these rules while matching
the existing database's examination maximum-score constraints.

## Remaining work

1. Decide and implement secure account storage and authentication.
2. Implement repository/service methods using the existing PostgreSQL schema.
3. Gate every data endpoint by authorization and connect GUI operations.
4. Verify student, programme, examination, result, reporting, and dashboard
   operations without seeding or overwriting existing records.
