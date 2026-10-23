# Implementation Plan: Expense Tracker

**Branch**: `001-expense-tracker` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-expense-tracker/spec.md`

## Summary

Provide a private, single-user expense tracker for recording and maintaining expenses,
reviewing monthly category totals with a separate chart, and setting category budgets.
Implement it as one local-only FastAPI app using SQLite, served HTML and plain
JavaScript, with pytest coverage and no frontend framework.

## Technical Context

**Language/Version**: Python 3.15

**Primary Dependencies**: FastAPI and Uvicorn; pytest and pip-audit for development checks

**Storage**: SQLite via Python's standard-library `sqlite3`; application-relative `expenses.db`

**Testing**: pytest with FastAPI `TestClient` and isolated temporary SQLite databases

**Target Platform**: Local machine; server binds to `127.0.0.1` and serves a same-origin browser UI

**Project Type**: Single-project web application

**Performance Goals**: Common list, monthly summary, and budget views complete within one second
on the development machine for a 10,000-expense test dataset.

**Constraints**: One user; no sign-in, network exposure, export, backup, or synchronization.
Use EUR, fixed categories, exact cents, validated ISO dates, and server-side input validation.
No frontend framework or chart dependency. Mutating requests are same-origin only.

**Scale/Scope**: One local user and an initial planning dataset of up to 10,000 expenses; one
FastAPI process, one SQLite database, one HTML page, and expense, summary, and budget flows.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Simplicity and stack discipline**: PASS. One Python 3.15 FastAPI app, SQLite, HTML, and
  plain JavaScript; no additional framework or service is introduced.
- **Validate all user input**: PASS. Validate amounts, dates/months, categories, booleans,
  filters, and notes at the server boundary; use parameterized SQL and database constraints.
- **Automated tests for every feature**: PASS. Pytest covers each user journey, invalid input,
  persistence, and derived totals before the feature is complete.
- **Specification-driven, verifiable changes**: PASS. Requirements and acceptance scenarios
  map to the contract and end-to-end validation guide.
- **Minimal dependencies and maintainable data**: PASS. Use standard-library SQLite, exact
  integer cents, and atomic transactions; audit dependencies before release.

**Gate result**: PASS. No constitution violations or complexity exceptions are required.
**Post-design gate**: PASS. The selected single-app structure, SQLite data model, same-origin
contracts, and pytest validation satisfy all constitution principles without added complexity.

## Project Structure

### Documentation (this feature)

```text
specs/001-expense-tracker/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/
│   └── api.md           # Same-origin HTTP contract
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Generated later by /speckit-tasks
```

### Source Code (repository root)

```text
app.py
static/
├── index.html
├── app.js
└── styles.css
tests/
└── test_app.py
requirements.txt
```

**Structure Decision**: Keep the application in one `app.py` module and serve the
framework-free browser interface from `static/`. Keep pytest integration tests in
`tests/test_app.py`. Do not introduce a separate frontend project, service layer package,
or ORM until a demonstrated requirement justifies the added structure.

