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
- Login uses Django authentication and DRF Token Authentication. Protected API
  endpoints require a token; the desktop client sends it in the
  `Authorization: Token ...` header and clears it after logout or a 401.
- The PyQt Student Management page uses the API for listing/search and
  student create, update, and delete operations. Its network work runs in a
  `QThread`; backend serializers validate input and database constraints.
- All GUI modules now use the API for listing/search, create, update, and
  delete operations through the `AppState` service layer.
- API access requires an active institution administrator token.
- The standalone console workflow continues to use its existing JSON files.
  Those files are not the PostgreSQL database and are not imported automatically.

## API contract

The frontend and backend now agree on field names and endpoint paths:

- Programmes: `programme_code`, `programme_name`, `description`, `is_active`
- Modules: `module_code`, `module_name`, `level`, `semester`, `description`, `is_active`, `programme_ids`
- Academic years: `academic_year_id`, `year_name`, `start_date`, `end_date`, `is_current`
- Examinations: `examination_code`, `examination_title`, `module_id`, `academic_year_id`, `examination_type`, `examination_date`, `maximum_score`, `duration_minutes`, `status`
- Questions: `question_text`, `question_type`, `options`, `correct_answer`, `marks`, `question_order`
- Results: `student_id`, `examination_id`, `score`, `grade`, `remarks`
- Students: `admission_number`, `first_name`, `last_name`, `age`, `gender`, `programme_id`, `is_active`

## Database schema relationships

- Students reference programmes.
- Programmes and modules are linked through `programme_modules`.
- Examinations reference modules and academic years.
- Questions belong to examinations.
- Exam results reference students and examinations.
- `result_audit` stores result change audit entries.

The PostgreSQL schema is authoritative. Do not run migrations or schema
initialization against it. Backend tests use a separate in-memory SQLite
database and test-only rows; they do not exercise production writes.

## Grading rules

The existing frontend `ExamResult` model accepts finite numeric scores from
0 through 100 and maps them to A (70+), B (60+), C (50+), D (40+), and F
(below 40). Backend result validation preserves these rules while matching the
existing database's examination maximum-score constraints.

## Remaining work

1. Define and implement role-based permissions, if different authenticated
   users should have different read/write access.
2. Perform production read/write verification only with an authorized account
   and a user-approved, reversible test plan; preserve all existing records.
