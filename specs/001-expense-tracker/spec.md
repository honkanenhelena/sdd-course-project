# Feature Specification: Expense Tracker

**Feature Branch**: `001-expense-tracker`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "An expense tracker that helps the user see what their money goes to and helps them cut costs. Users can add, edit, delete, and filter expenses; see monthly summaries and category charts; and set monthly category budgets. Invalid amounts and dates must be rejected, required fields enforced, and data saved consistently for ongoing monthly use."

## Clarifications

### Session 2026-10-22

- Q: Will this tracker be a private single-user app, or will it be accessible to multiple users over a network? → A: Private single-user app with no accounts or sign-in.
- Q: Should users be able to export saved expenses and budgets as a backup? → A: No export or backup.
- Q: Which currency should the tracker use for all expenses and budgets? → A: EUR.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record and Maintain Expenses (Priority: P1)

A user records each purchase with its amount, date, category, whether it was a necessity, and an optional note. The user can later correct or remove a record.

**Why this priority**: Expense records are the source of all spending views and budget calculations.

**Independent Test**: Add an expense, verify it appears in the expense list, edit its details, then delete it and verify it is removed.

**Acceptance Scenarios**:

1. **Given** the expense list is available, **When** the user submits a valid amount, date, category, necessity choice, and optional note, **Then** the expense appears with the submitted details.
2. **Given** an existing expense, **When** the user edits and saves its amount, date, category, necessity choice, or note, **Then** the list shows the updated values.
3. **Given** an existing expense, **When** the user confirms deletion, **Then** it is removed from the list and no longer contributes to spending totals.
4. **Given** a required field is missing or the amount or date is invalid, **When** the user attempts to save the expense, **Then** the user is told what must be corrected and no invalid record is saved.
5. **Given** the user opens the category choices, **When** the list is displayed, **Then** it contains Housing (`housing`), Utilities (`utilities`), Groceries (`groceries`), Transport (`transport`), Health (`health`), Dining (`dining`), Shopping (`shopping`), Entertainment (`entertainment`), and Other (`other`), with no category-creation or rename controls.

---

### User Story 2 - Understand Monthly Spending (Priority: P2)

A user reviews expenses for a chosen period and understands where money went through filters, a monthly category breakdown, and a separate category spending chart.

**Why this priority**: Reviewing categorized spending helps the user identify patterns and possible cost reductions.

**Independent Test**: Add expenses across dates and categories, select a month and filters, and compare the displayed list, category totals, and chart with the known records.

**Acceptance Scenarios**:

1. **Given** saved expenses, **When** the user selects a date range, category, and/or necessity status, **Then** the list contains only expenses matching every selected filter.
2. **Given** saved expenses for a calendar month, **When** the user opens that month's summary, **Then** the total and category breakdown equal the expenses recorded in that month.
3. **Given** a monthly category breakdown, **When** the user views the separate spending chart, **Then** each displayed category and value corresponds to that month's category spending.
4. **Given** a month with no expenses, **When** the user opens its summary, **Then** the summary and chart clearly show that no spending has been recorded.

---

### User Story 3 - Set and Monitor Category Budgets (Priority: P3)

A user sets a spending limit for a category in a month and checks how much of that limit has been used or remains.

**Why this priority**: Budgets build on reliable expense records and monthly totals, and help users act on the patterns they identify.

**Independent Test**: Set a category limit, add expenses in that category and month, and verify the used, remaining, and exceeded amounts.

**Acceptance Scenarios**:

1. **Given** a month and category, **When** the user saves a valid budget amount, **Then** the budget is associated with that category and month.
2. **Given** a saved budget and matching expenses, **When** the user views the budget, **Then** the displayed spending, remaining amount, and progress accurately reflect those expenses and the limit.
3. **Given** category spending exceeds its budget, **When** the user views the budget, **Then** the view indicates that the limit has been exceeded and by how much.
4. **Given** the user returns to a previously budgeted month, **When** the user opens its budget view again, **Then** the saved budget and current progress are still available.

### Edge Cases

- Missing amount, date, or category is rejected without saving a partial expense.
- Zero or negative amounts and amounts with more than two fractional digits are rejected.
- Impossible calendar dates and malformed dates are rejected.
- A date range with its start after its end is rejected with HTTP 422 and a clear date-range error message; no expense results are returned.
- Combining filters returns only records that satisfy all selected filters; an unset filter does not restrict results.
- Deleting or editing an expense updates the affected monthly totals, chart, and budget progress.
- A category with no expenses still appears in budget progress with zero spent.
- Spending equal to a budget is shown as fully used, not exceeded; spending above it shows the overage.
- Empty notes are allowed and do not prevent saving an otherwise valid expense.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a user to record an expense with an amount in EUR, date, category, necessity choice, and optional note.
- **FR-002**: The system MUST require an amount, a valid date, and a category before saving an expense.
- **FR-003**: The system MUST reject zero or negative expense amounts, amounts with more than two fractional digits, and dates that are malformed or impossible calendar dates. Rejected data MUST NOT be saved.
- **FR-004**: The system MUST allow a user to edit or delete a saved expense, and changes MUST be reflected in all spending views.
- **FR-005**: The system MUST allow expenses to be filtered by inclusive date range, category, and necessity status. When multiple filters are selected, all selected conditions MUST apply.
- **FR-006**: The system MUST provide a monthly summary showing total spending and a breakdown by category for the selected calendar month.
- **FR-007**: The system MUST provide a separate spending chart that visualizes category amounts for the selected month and agrees with the monthly category breakdown.
- **FR-008**: The system MUST allow a user to set a positive spending limit for a category in a selected month.
- **FR-009**: The system MUST show each budget's amount spent, amount remaining or exceeded, and progress relative to its limit for that category and month.
- **FR-010**: The system MUST preserve expenses and monthly category budgets when the user leaves and returns, including when viewing a different month.
- **FR-011**: The system MUST provide clear feedback when input is missing, invalid, or inconsistent, without saving invalid data.
- **FR-012**: The system MUST offer these fixed category choices and slugs: Housing (`housing`), Utilities (`utilities`), Groceries (`groceries`), Transport (`transport`), Health (`health`), Dining (`dining`), Shopping (`shopping`), Entertainment (`entertainment`), and Other (`other`). Users MUST NOT be able to create or rename categories.

### Key Entities *(include if feature involves data)*

- **Expense**: A purchase record with an amount, date, category, necessity status, and optional note.
- **Category**: A label used to group expenses and associate a monthly spending limit.
- **Monthly Category Budget**: A spending limit associated with one category and one calendar month.
- **Monthly Summary**: A view derived from expenses in one calendar month, including total and per-category spending.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time user can add an expense to the app without further instructions.
- **SC-002**: For every tested combination of date, category, and necessity filters, the results contain exactly the matching expenses and no non-matching expenses.
- **SC-003**: For every tested month, the displayed total and category amounts equal the sum of the saved expenses in that month, and the chart shows the same category amounts.
- **SC-004**: 100% of tested missing required fields, zero or negative amounts, over-precision amounts, malformed dates, and impossible dates are rejected without creating or changing a saved expense.
- **SC-005**: For every tested category and month, displayed budget progress equals the matching expense total and correctly reports the remaining amount or overage, including after leaving and returning to the view.

## Assumptions

- The tracker is a private single-user app with no accounts or sign-in; network access, sharing, and multi-user permissions are outside this feature's scope.
- All expenses and budgets use EUR; currency conversion and multi-currency reporting are out of scope.
- The fixed purchase categories are Housing (`housing`), Utilities (`utilities`), Groceries (`groceries`), Transport (`transport`), Health (`health`), Dining (`dining`), Shopping (`shopping`), Entertainment (`entertainment`), and Other (`other`). Creating or renaming categories is out of scope for this feature.
- A budget is specific to one category and one calendar month; it does not automatically carry into other months.
- Expense amounts and budgets must be greater than zero and may have at most two fractional digits.
- Dates are validated as real calendar dates. Future dates are not otherwise restricted.
- Deletion requires user confirmation to reduce accidental removal.
- Expenses and budgets remain available across normal sessions; export, backup, and synchronization are outside this feature's scope.
