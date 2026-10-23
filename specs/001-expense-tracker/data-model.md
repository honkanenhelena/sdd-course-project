# Data Model: Expense Tracker

## Storage

The application uses one SQLite database at a stable path next to the application (default: `expenses.db`). The path is resolved from the application location, not the current working directory. One connection is opened for each request, all values are bound parameters, writes use explicit transactions, and connections are closed after the request. A failed write rolls back completely.

Money is represented as integer EUR cents in storage and calculations. API inputs and outputs use decimal strings such as `"12.34"`; no floating-point arithmetic is used for money. Expense dates use ISO calendar-date strings (`YYYY-MM-DD`). Budget months use `YYYY-MM`.

## Category

The category vocabulary is fixed in the application and is not user-managed in this feature.

| Slug | Display label |
|---|---|
| `housing` | Housing |
| `utilities` | Utilities |
| `groceries` | Groceries |
| `transport` | Transport |
| `health` | Health |
| `dining` | Dining |
| `shopping` | Shopping |
| `entertainment` | Entertainment |
| `other` | Other |

The API accepts category slugs and returns both slug and display label. Unknown slugs are rejected.

## Expense

A purchase record is persisted in the `expenses` table.

| Field | Type | Required | Rules |
|---|---|---:|---|
| `id` | integer | generated | Stable primary key |
| `amount_cents` | integer | yes | Greater than zero; input has at most two fractional digits |
| `spent_on` | text | yes | Real calendar date in exact `YYYY-MM-DD` form |
| `category` | text | yes | One of the fixed category slugs |
| `is_necessity` | integer/boolean | yes | Exactly true or false |
| `note` | text | no | Optional; empty text is valid and is not truncated |

The database enforces non-null required fields, positive cents, and a boolean domain for `is_necessity`. The application validates date reality and exact format before writing. A note may be `null` or text; the application does not silently truncate user content.

### Lifecycle

- Creation validates the complete required expense data before inserting a row.
- Replacement updates all editable fields only after validating the complete replacement object.
- Deletion removes the selected expense after the user confirms in the interface.
- Every mutation is atomic. Subsequent summaries and budget progress are derived from current expense rows, so no cached totals require synchronization.

## Monthly Category Budget

One spending limit is stored for each category and calendar month in `monthly_budgets`.

| Field | Type | Required | Rules |
|---|---|---:|---|
| `month` | text | yes | Exact `YYYY-MM` form for a real calendar month |
| `category` | text | yes | One of the fixed category slugs |
| `amount_cents` | integer | yes | Greater than zero |

The composite primary key `(month, category)` guarantees at most one budget for each category/month pair. Saving a new value for an existing pair replaces that pair's amount. Budgets do not carry forward to another month.

For a month/category pair, `spent_cents` is the sum of matching expenses within the month. `remaining_cents` is `max(budget_cents - spent_cents, 0)` and `overage_cents` is `max(spent_cents - budget_cents, 0)`. Exactly reaching the limit is fully used with zero overage.

## Monthly Summary (Derived)

The summary is not stored independently. It is derived for one calendar month from expense rows and includes:

- `month` in `YYYY-MM` form
- total spending in EUR
- one row per fixed category with its label and spending, including zero-spend categories
- the same category amounts used by the separate chart

Month selection uses a half-open date interval from the first day of the selected month to the first day of the following month. This avoids timezone conversion and month-end boundary errors.

## Validation and Consistency

- Amounts arrive as decimal strings, must be finite and positive, and may have at most two fractional digits. They are converted exactly to integer cents.
- Dates must be exact ISO date strings and valid calendar dates. Future dates are allowed.
- Budget months must be exact, valid `YYYY-MM` values; budget amounts must be positive.
- Categories must match the fixed vocabulary; necessity must be a boolean; notes must be text or null.
- Invalid input is rejected before persistence and does not change existing data.
- SQLite `NOT NULL`, `CHECK`, and unique-key constraints protect core invariants in addition to API validation.
- Summary, chart, and budget values are recalculated from stored expenses so edits and deletions are reflected immediately.
