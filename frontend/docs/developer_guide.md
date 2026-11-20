# Developer Guide

## Environment setup

Use Python 3 and the dependency listed in `frontend/requirements.txt`:

```powershell
cd frontend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the desktop application from the repository root with `python main.py`.
Run the console workflow from `frontend/` with `python main.py --console`.

The root `main.py` launcher starts the app with `frontend/` as its working
directory, keeping the desktop JSON files there.

## Code organization

Keep the current OOP architecture and GUI package structure:

- Domain entities and grade rules are in the `frontend/` Python modules.
- JSON record I/O is handled by `storage.RecordStore`.
- GUI startup, state, styling, windows, pages, and shared widgets live under
  `frontend/gui/`.
- The Django REST backend lives under `backend/`; it has its own
  `requirements.txt`, ignored environment configuration, and unmanaged ORM
  mappings to the existing PostgreSQL schema. See
  [backend/README.md](../../backend/README.md) for setup and safety notes.
- The CLI and application dispatcher are in `frontend/main.py`; root
  `main.py` remains a compatibility launcher.

Keep presentation code in GUI modules and domain validation in model or
business-logic functions. Before moving a module, search all imports and tests,
preserve the current CLI entry point, and update documentation in the same
approved change.

## Tests and checks

Run the frontend test suite from `frontend/`:

```powershell
python -m unittest discover -v
```

The frontend tests cover API token handling, login success/failure, student
field mapping, asynchronous student listing, and score validation. The GUI
tests use PyQt6's offscreen platform when no platform override is set.

When changing data handling, add tests for missing, valid, and malformed
persisted data. When changing a GUI flow, cover both the success and failure
paths and verify that the dashboard navigation remains operational.

For backend changes, run checks from `backend/` after installing its
`requirements.txt` and creating `.env` from `.env.example`:

```powershell
python manage.py check
python manage.py test --settings=config.test_settings
```

The test settings use an isolated in-memory SQLite database for test-only
unmanaged-table fixtures. Do not run production database writes as routine
tests.

## Persistence safety

- Back up JSON data before any migration or bulk edit.
- The console workflow uses JSON in `frontend/`. The backend maps the existing
  PostgreSQL database and does not create or migrate its tables. The retained
  `frontend/instance/exam_portal.db` is not used by the backend.
- Avoid changing file paths or formats without a compatibility/migration plan.
- Prefer explicit errors over silently presenting empty data when persistence
  fails.
- Consider atomic replacement and UTF-8 encoding for future JSON-write
  improvements, with tests before rollout.
- Do not place real student information or credentials in source control.

## Repository hygiene

The root `.gitignore` excludes Python bytecode/cache directories and local
virtual environments. It deliberately does not ignore JSON files or the
existing SQLite file, so data and legacy artifacts remain visible for review.

The repository currently has pre-existing worktree changes and untracked
artifacts. Review `git status` before staging or making structural changes, and
do not discard unrelated changes. Tracked bytecode artifacts are not removed
by `.gitignore`; any removal from version control should be handled separately
and reviewed.

## Current technical debt

- `frontend/gui/app_state.py` imports `build_programme_catalogue` from the CLI-oriented
  `main.py`.
- Several persistence operations use current-working-directory paths.
- JSON writes are not atomic, and some load errors use silent fallback values.
- Existing tests do not yet cover all GUI pages, JSON persistence, or CSV
  export.
- DRF token authentication is enabled. API endpoints currently apply
  authenticated-user access without finer role-based authorization.

Address these items incrementally. Do not access PostgreSQL directly from
frontend code; all GUI data must go through the backend API.
