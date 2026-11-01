# HTTP API Contract: Expense Tracker

All endpoints are served by the same FastAPI application and origin as the HTML interface. The application listens on loopback only. JSON request and response bodies use UTF-8. Monetary fields are decimal strings in EUR (for example, `"12.34"`); they are never JSON floating-point values. Dates are calendar dates in `YYYY-MM-DD`; months use `YYYY-MM`.

## Common Behavior

- Malformed JSON, missing required data, unknown categories, malformed dates/months, non-finite or non-positive amounts, and amounts with more than two fractional digits return `422` with a field-specific validation message.
- Missing records return `404`.
- Successful deletion returns `204` with no response body.
- State-changing methods accept same-origin requests only. Cross-origin requests are not enabled.
- API responses do not expose internal database paths or stack traces.

## Categories

### `GET /api/categories`

Returns the fixed category vocabulary in display order.

```json
[
  {"id": "housing", "label": "Housing"},
  {"id": "utilities", "label": "Utilities"},
  {"id": "groceries", "label": "Groceries"},
  {"id": "transport", "label": "Transport"},
  {"id": "health", "label": "Health"},
  {"id": "dining", "label": "Dining"},
  {"id": "shopping", "label": "Shopping"},
  {"id": "entertainment", "label": "Entertainment"},
  {"id": "other", "label": "Other"}
]
```

## Expenses

An expense response has this shape:

```json
{
  "id": 1,
  "amount": "12.34",
  "currency": "EUR",
  "date": "2026-10-22",
  "category": "groceries",
  "category_label": "Groceries",
  "is_necessity": true,
  "note": "Weekly food shop"
}
```

### `GET /api/expenses`

Returns expenses ordered by date descending, then id descending. Optional query parameters:

- `from`: inclusive `YYYY-MM-DD` lower bound
- `to`: inclusive `YYYY-MM-DD` upper bound
- `category`: one fixed category slug
- `necessity`: `true` or `false`

All supplied filters apply together. If `from` is after `to`, return `422` with the response `{"detail":"The start date must be on or before the end date."}`. No expense results are returned for this invalid range. With no filters, return all expenses.

### `POST /api/expenses`

Creates an expense; returns `201` and the created expense.

```json
{
  "amount": "12.34",
  "date": "2026-10-22",
  "category": "groceries",
  "is_necessity": true,
  "note": "Weekly food shop"
}
```

`amount`, `date`, `category`, and `is_necessity` are required. `note` is optional and may be null or an empty string.

### `PUT /api/expenses/{expense_id}`

Replaces all editable fields of an existing expense. The body uses the same shape and validation rules as `POST`; returns `200` and the updated expense.

### `DELETE /api/expenses/{expense_id}`

Deletes an existing expense; returns `204`. The browser asks for confirmation before calling this endpoint.

## Monthly Summary and Chart Data

### `GET /api/summary?month=YYYY-MM`

Returns a summary for exactly one calendar month. `month` is required and must identify a real month.

```json
{
  "month": "2026-10",
  "currency": "EUR",
  "total": "84.50",
  "categories": [
    {"id": "housing", "label": "Housing", "total": "0.00"},
    {"id": "utilities", "label": "Utilities", "total": "0.00"},
    {"id": "groceries", "label": "Groceries", "total": "84.50"},
    {"id": "transport", "label": "Transport", "total": "0.00"},
    {"id": "health", "label": "Health", "total": "0.00"},
    {"id": "dining", "label": "Dining", "total": "0.00"},
    {"id": "shopping", "label": "Shopping", "total": "0.00"},
    {"id": "entertainment", "label": "Entertainment", "total": "0.00"},
    {"id": "other", "label": "Other", "total": "0.00"}
  ]
}
```

The response contains every fixed category, including zero values. The same `categories` values feed the textual breakdown and the separate labeled bar chart. With no expenses, totals are `"0.00"` and category totals are zero.

## Monthly Budgets

A budget response has this shape:

```json
{
  "month": "2026-10",
  "category": "groceries",
  "category_label": "Groceries",
  "limit": "250.00",
  "spent": "84.50",
  "remaining": "165.50",
  "overage": "0.00",
  "progress_percent": 33.8,
  "currency": "EUR"
}
```

`progress_percent` is `spent / limit * 100` and may exceed 100. Remaining and overage are non-negative; only one may be non-zero.

### `GET /api/budgets?month=YYYY-MM`

Returns budgets for the selected month with current spending progress. The month is required and must be valid.

### `PUT /api/budgets/{month}/{category}`

Creates or replaces the limit for the month/category pair; returns `200` and the current budget progress. The body is:

```json
{"limit": "250.00"}
```

The limit must be a finite positive EUR amount with at most two fractional digits. Invalid months and categories are rejected.

## Browser Interface

- `GET /` serves the expense tracker HTML document.
- Static JavaScript and CSS are served from the same origin.
- User-provided note text is rendered as text, never interpreted as HTML.
- The chart has visible category labels and values; it does not rely on color alone.
