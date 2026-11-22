# API Documentation

All protected endpoints use `Authorization: Token <token>`.
Institution administrators have administrative access. Institution staff can read academic data and create/update students and results, but cannot delete students or results or mutate programmes, modules, examinations, questions, or institution settings.

## Authentication

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| GET | `/api/auth/registration-status/` | Check whether initial registration is open | Public |
| POST | `/api/auth/register/` | Register the first institution administrator | Public |
| POST | `/api/auth/login/` | Obtain an account token | Public |
| POST | `/api/auth/logout/` | Revoke the current token | Authenticated |
| GET | `/api/auth/me/` | Retrieve the current account and institution | Authenticated |
| PATCH | `/api/auth/institution/` | Update the institution name | Institution administrator |
| GET/POST | `/api/auth/admins/` | List or provision administrators | Institution administrator |
| PATCH | `/api/auth/admins/<user_id>/` | Activate or deactivate an administrator | Institution administrator |

Tokens expire after 12 hours.

## Academic records

| Method | Endpoint | Access |
|---|---|---|
| GET/POST | `/api/students/` | Staff or administrator; POST creates a student |
| GET/PUT/DELETE | `/api/students/<student_id>/` | Staff/admin for GET/PUT; administrator for DELETE |
| GET/POST | `/api/programmes/` | Readable by institution users; POST administrator-only |
| GET/PUT/DELETE | `/api/programmes/<programme_id>/` | GET institution users; mutations administrator-only |
| GET/POST | `/api/modules/` | Readable by institution users; POST administrator-only |
| GET/PUT/DELETE | `/api/modules/<module_id>/` | GET institution users; mutations administrator-only |
| GET/POST | `/api/examinations/` | Readable by institution users; POST administrator-only |
| GET/PUT/DELETE | `/api/examinations/<examination_id>/` | GET institution users; mutations administrator-only |
| GET/POST | `/api/examinations/<examination_id>/questions/` | Institution user for GET; administrator for POST |
| GET/PUT/DELETE | `/api/questions/<question_id>/` | Institution user for GET; administrator for mutations |
| GET/POST | `/api/results/` | Staff or administrator |
| GET/PUT/DELETE | `/api/results/<result_id>/` | Staff/admin for GET/PUT; administrator for DELETE |
| GET | `/api/reports/` | Institution user |
| GET | `/api/dashboard/` | Institution user |

## Student request body

```json
{
  "admission_number": "ADM-001",
  "first_name": "Ada",
  "last_name": "Example",
  "age": 20,
  "gender": "Female",
  "programme_id": 1
}
```

`gender` may be `Male`, `Female`, `Other`, or null.

## Institution update request body

```json
{
  "institution_name": "Limkokwing University"
}
```

An empty name is rejected with HTTP 400.
An unauthenticated request is rejected with HTTP 401.
A non-administrator request is rejected with HTTP 403.

Question types are accepted as `mcq`, `true_false`, or `short_answer` (the
database stores `MCQ`, `TRUE_FALSE`, or `SHORT_ANSWER`). Examination reads
include their questions; only institution administrators receive the
`correct_answer` field.

Result grades are based on the score as a percentage of the examination's
`maximum_score`. PostgreSQL triggers calculate the stored grade and write
audit rows when a result is updated or deleted.
