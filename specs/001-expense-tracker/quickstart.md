# Quickstart: Expense Tracker Validation

## Prerequisites

- Python 3.15 installed.
- A terminal opened at the repository root.

## Setup and Run

```sh
python3.15 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`. The app must remain bound to loopback; do not expose it on a network interface. The database is created at the stable application-relative path described in [data-model.md](data-model.md).

## Automated Checks

In a second terminal, activate the same environment and run:

```sh
python -m pytest -q
python -m pip_audit -r requirements.txt
```

Expected: all pytest tests pass, including invalid-input and persistence tests; the dependency audit reports no known unresolved vulnerabilities (or any accepted finding is explicitly reviewed before release).

## End-to-End Scenarios

1. **Record and persist an expense**: Add an expense for `12.34` EUR dated `2026-10-22`, category `groceries`, mark it as a necessity, and add a note. Confirm it appears in the expense list. Restart the app and confirm the record remains.
2. **Validate input**: Attempt to save an expense with a negative amount, a value with more than two fractional digits, a missing required field, and an impossible date such as `2026-02-30`. Each attempt must show a useful error and leave saved data unchanged. Apply a date filter whose start is after its end; expect HTTP 422 with `The start date must be on or before the end date.`
3. **Filter and summarize**: Add expenses on different dates and in different categories. Select an inclusive date range and combine it with category and necessity filters. Confirm only matching rows remain. Open `2026-10`; confirm the displayed total and category values equal the saved October expenses.
4. **Compare chart and breakdown**: View the separate category chart for `2026-10`. Confirm each labeled bar uses the same amount as its category breakdown entry, including zero-spend categories.
5. **Monitor a budget**: Set the October groceries limit to `50.00` EUR. Confirm spent, remaining, and progress match the groceries expenses. Add or edit an expense to exceed the limit and confirm overage is shown. Change to another month and back; confirm the October budget remains.
6. **Edit and delete**: Edit an expense and confirm list, summary, chart, and budget progress update. Confirm deletion in the interface and verify the expense no longer contributes to any total.
7. **First-time use**: Ask a first-time user to add an expense without instructions; confirm the user can complete the task and see the expense in the list.

## Contract References

See [api.md](contracts/api.md) for request/response shapes and status behavior, and [data-model.md](data-model.md) for persistence and validation rules.
