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

## Current technical debt

- `frontend/gui/app_state.py` imports `build_programme_catalogue` from the CLI-oriented
  `main.py`.
- Several persistence operations use current-working-directory paths.
- JSON writes are not atomic, and some load errors use silent fallback values.
- Existing tests do not yet cover all GUI pages, JSON persistence, or CSV
  export.
- DRF token authentication is enabled. API endpoints require an active
  institution administrator role; finer role-based authorization is not yet
  implemented.

Address these items incrementally. Do not access PostgreSQL directly from
frontend code; all GUI data must go through the backend API.
