# Tasks: Expense Tracker

**Input**: Design documents from `specs/001-expense-tracker/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/api.md`, and `quickstart.md`

**Tests**: Included for all three user stories because the project constitution requires automated pytest coverage for every feature. Write each story's tests first and verify they fail before implementing that story.

**Organization**: Tasks are grouped by user story so each increment can be verified independently after shared setup.

## Phase 1: Setup

**Purpose**: Add the runtime/development dependencies and the planned static UI shell.

- [ ] T001 [P] Add FastAPI, Uvicorn, pytest, and pip-audit dependencies in `requirements.txt`.
- [ ] T002 [P] Create the HTML document shell in `static/index.html`, the empty plain-JavaScript entry point in `static/app.js`, and the base stylesheet in `static/styles.css`.

---

## Phase 2: Foundational

**Purpose**: Provide the local application, persistent database, shared validation, and isolated test fixture required by every story.

- [ ] T003 Create the FastAPI app factory and static-file mount in `app.py`; bind the documented runner to `127.0.0.1`, accept only loopback Host values, and require same-origin Origin values for browser mutation requests.
- [ ] T004 Initialize the stable application-relative SQLite database and implement per-request connections, parameterized access, explicit write transactions, rollback on failure, and connection closing in `app.py`.
- [ ] T005 Create the `expenses` and `monthly_budgets` schema with the data-model constraints in `app.py`, including positive integer cents, required fields, a boolean necessity domain, and the unique `(month, category)` budget key.
- [ ] T006 Add the fixed category list and shared validators in `app.py`; enforce these exact category slugs: `housing`, `utilities`, `groceries`, `transport`, `health`, `dining`, `shopping`, `entertainment`, and `other`; finite positive EUR values with at most two fractional digits; real ISO `YYYY-MM-DD` dates; valid `YYYY-MM` months; and necessity values that are exactly true or false. Preserve the data-model note constraint verbatim: `note` is optional; empty text is valid and is not truncated.
- [ ] T007 Create a pytest fixture in `tests/test_app.py` that builds the app with a fresh `tmp_path` database and provides a FastAPI `TestClient` without touching the user's `expenses.db`.

**Checkpoint**: App startup, schema creation, shared validation, and isolated test setup are ready before story work begins.

---

## Phase 3: User Story 1 - Record and Maintain Expenses (Priority: P1) - MVP

**Goal**: Create, list, edit, and delete validated expenses with persistent storage.

**Independent Test**: Using the test client and a fresh SQLite database, create an expense, retrieve it, replace its fields, delete it, and verify that invalid submissions are rejected without changing stored data.

### Tests and Implementation for Category Choices

- [ ] T008 [US1] Add a pytest test in `tests/test_app.py` for `GET /api/categories`; assert it returns the nine exact fixed category slugs and display labels in the order defined by `spec.md`, and confirm the test fails before implementation.
- [ ] T009 [US1] Implement `GET /api/categories` in `app.py`; return the fixed slug/label list from `data-model.md` in the order defined by `spec.md`.

### Tests for Expense Records

- [ ] T010 [US1] Add pytest API tests in `tests/test_app.py` for expense creation/listing, full replacement, deletion, missing fields, invalid/over-precision/non-positive amounts, malformed/impossible dates, unknown categories, and unchanged data after rejected writes; confirm the tests fail before implementation.

### Implementation for User Story 1

- [ ] T011 [P] [US1] Implement `GET /api/expenses`, `POST /api/expenses`, `PUT /api/expenses/{expense_id}`, and `DELETE /api/expenses/{expense_id}` in `app.py`; return decimal-string EUR amounts, use status codes from `contracts/api.md`, and commit each mutation atomically.
- [ ] T012 [P] [US1] Add the expense entry form, required-field indicators, filter/list region, edit controls, and delete-confirmation affordance to `static/index.html`.
- [ ] T013 [P] [US1] Style the expense form, list, validation feedback, and confirmation state with responsive, accessible HTML control states in `static/styles.css`.
- [ ] T014 [US1] Implement category-choice loading from `GET /api/categories`, expense creation, full-field editing, confirmed deletion, list refresh, and safe text rendering with `textContent` in `static/app.js`; display field-specific API validation errors without clearing valid user input.

**Checkpoint**: A user can persist, view, edit, and remove expenses; rejected values never create or mutate a row.

---

## Phase 4: User Story 2 - Understand Monthly Spending (Priority: P2)

**Goal**: Filter saved expenses and inspect an accurate monthly total, category breakdown, and separate category chart.

**Independent Test**: Seed expenses across month boundaries, categories, and necessity values; verify combined inclusive filters, monthly totals, zero-spend categories, and agreement between the category breakdown and chart.

### Tests for User Story 2

- [ ] T015 [US2] Add pytest API tests in `tests/test_app.py` for inclusive date boundaries, combined date/category/necessity filters, and a reversed range returning HTTP 422 with `{"detail":"The start date must be on or before the end date."}`; also test month boundaries, empty months, and every category total, and confirm the tests fail before implementation.

### Implementation for User Story 2

- [ ] T016 [P] [US2] Implement validated expense filters and `GET /api/summary?month=YYYY-MM` in `app.py`; apply all selected filters, return HTTP 422 with the exact date-range error from `contracts/api.md` when `from` is after `to`, use half-open calendar-month bounds, and return all fixed categories with exact decimal-string totals.
- [ ] T017 [P] [US2] Add month selection, inclusive date-range filters, category and necessity filters, monthly total, and category breakdown regions in `static/index.html`.
- [ ] T018 [P] [US2] Implement filter requests, monthly summary loading, empty-state feedback, and a labeled horizontal category chart from the authoritative summary response in `static/app.js`; render exact values and do not rely on color alone.
- [ ] T019 [P] [US2] Style the filters, monthly summary, category breakdown, and labeled chart in `static/styles.css`, including a readable narrow-screen layout.

**Checkpoint**: Filtered lists, monthly totals, category breakdown, and chart agree with persisted records, including empty months.

---

## Phase 5: User Story 3 - Set and Monitor Category Budgets (Priority: P3)

**Goal**: Set one positive EUR limit per category/month and see current spending, remaining amount, overage, and progress.

**Independent Test**: Set a monthly category limit, add/edit/delete matching expenses, and verify spent, remaining, overage, and progress at below, equal-to, and above-budget values.

### Tests for User Story 3

- [ ] T020 [US3] Add pytest API tests in `tests/test_app.py` for valid/invalid budget amounts, invalid months/categories, create-or-replace behavior, one budget per `(month, category)`, zero-spend progress, and recalculation after expense edits/deletes; confirm they fail before implementation.

### Implementation for User Story 3

- [ ] T021 [P] [US3] Implement `GET /api/budgets?month=YYYY-MM` and `PUT /api/budgets/{month}/{category}` in `app.py`; enforce positive EUR cents, valid month/category, atomic create-or-replace, and exact spent/remaining/overage calculations.
- [ ] T022 [P] [US3] Add a month/category budget form and a budget progress region with limit, spent, remaining, and exceeded values in `static/index.html`.
- [ ] T023 [US3] Implement budget loading and saving, progress refresh after expense changes, and clear over-limit messaging in `static/app.js`.
- [ ] T024 [P] [US3] Style budget forms and progress indicators in `static/styles.css`; distinguish under-limit, fully used, and exceeded states with text as well as visual treatment.

**Checkpoint**: Each monthly category budget persists and reflects current expenses, including exact-limit and over-limit cases.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Verify persistence/security boundaries, dependency health, and the complete quickstart workflow.

- [ ] T025 Add pytest regression tests in `tests/test_app.py` for persistence across app recreation, database constraint enforcement/rollback, loopback Host handling, same-origin mutation checks, and root/static asset delivery.
- [ ] T026 Run `python -m pip_audit -r requirements.txt`, review each finding, and resolve or explicitly document accepted risks in `requirements.txt`.
- [ ] T027 Execute every scenario in `quickstart.md` against the completed application, including the first-time user adding an expense without further instructions, and update the guide at `specs/001-expense-tracker/quickstart.md` if any command or expected result differs.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 and T002 are independent and may start immediately.
- **Foundational (Phase 2)**: Depends on setup; completes before any story. Database and validation work precede the test fixture that uses the app factory and schema.
- **User Story 1 (Phase 3)**: Depends on the foundation and delivers the expense CRUD MVP.
- **User Story 2 (Phase 4)**: Depends on US1 because its filters, summary, and chart derive from saved expenses.
- **User Story 3 (Phase 5)**: Depends on US1 because budgets calculate from saved expenses. It is scheduled after US2 to avoid concurrent edits to the single `app.py`, `static/app.js`, and `tests/test_app.py` files.
- **Polish (Phase 6)**: Depends on the selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2; no dependency on another story.
- **US2 (P2)**: Requires US1 expense persistence and categories.
- **US3 (P3)**: Requires US1 expense persistence and categories; it does not require US2 summary functionality.

### Parallel Opportunities

- **Setup**: T001 (`requirements.txt`) and T002 (`static/index.html`, `static/app.js`, `static/styles.css`) can run in parallel.
- **US1**: Complete T008 before T009. Then complete T010 before T011; T012 (`static/index.html`) can proceed after T008. Once T012 establishes the UI selectors, T013 (`static/styles.css`) and T014 (`static/app.js`) can proceed in parallel.
- **US2**: After T015 tests are written and observed failing, T016 (`app.py`) and T017 (`static/index.html`) can run in parallel. After the markup is set, T018 (`static/app.js`) and T019 (`static/styles.css`) can proceed in parallel.
- **US3**: After T020 tests are written and observed failing, T021 (`app.py`) and T022 (`static/index.html`) can run in parallel. After the markup is set, T023 (`static/app.js`) and T024 (`static/styles.css`) can proceed in parallel.
- User story phases are kept sequential in the recommended single-developer flow because the plan intentionally uses one backend and one browser entry-point file.

## Implementation Strategy

### MVP First

1. Complete Phase 1 setup and Phase 2 foundation.
2. Complete US1 and stop to validate category choices, expense creation, listing, editing, deletion, persistence, and invalid-input rejection with pytest.
3. Deliver US1 as the smallest usable increment; do not require summaries or budgets for the CRUD MVP.

### Incremental Delivery

1. Add US2 after the expense MVP; validate combined filters, reversed-range HTTP 422 behavior, monthly totals, and chart agreement.
2. Add US3 after expense persistence; validate monthly budgets and recalculation after expense mutations.
3. Complete Phase 6 dependency audit and end-to-end quickstart verification.

### Independent Test Criteria by Story

- **US1**: API tests verify the fixed category choices and create, retrieve, replace, and delete an expense; invalid or missing values return validation errors and leave the database unchanged.
- **US2**: API tests prove inclusive filters and exact month/category totals; the browser shows the same monthly category values in the breakdown and chart, including an empty month.
- **US3**: API tests prove one budget per category/month and exact remaining/overage calculations; changing or deleting an expense updates the displayed progress.
