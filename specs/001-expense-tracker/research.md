# Research: Expense Tracker

## Decisions

### Single-process, local-only application

- **Decision**: Run one FastAPI application bound to `127.0.0.1`, serve the HTML/JavaScript from the same origin, disable cross-origin access, and allow only loopback Host values. Check the request Origin on state-changing requests.
- **Rationale**: The clarified scope is private, single-user, and has no sign-in. Binding to loopback keeps the application off the network without adding an account system. Same-origin requests avoid unnecessary CORS configuration.
- **Alternatives considered**: Network binding with user authentication adds deployment and identity scope that the user excluded. Binding to all interfaces without authentication would expose private financial records and mutation endpoints.

### SQLite access and persistence

- **Decision**: Use Python's standard-library `sqlite3` from synchronous FastAPI route handlers. Open a connection for each request, use parameterized statements and explicit transactions for writes, then close the connection. Keep the database at a stable path under the project data directory, independent of the process working directory.
- **Rationale**: SQLite meets the one-user, local-persistence requirement without a database service or ORM dependency. Per-request connections avoid unsafe global connection sharing; transactions keep each mutation atomic.
- **Alternatives considered**: A shared global connection risks concurrent access and unclear lifetime. SQLAlchemy or a separate database server adds abstractions and dependencies not warranted by this scope.

### Exact money and date representation

- **Decision**: Accept monetary input as a decimal string, validate it with `Decimal`, require a finite positive value with no more than two fractional digits, convert it to integer EUR cents, and use integer cents for storage, totals, and comparisons. Return amounts in JSON as decimal strings. Store expense dates as validated ISO `YYYY-MM-DD` calendar dates and budget periods as `YYYY-MM`.
- **Rationale**: Integer cents make totals and budget comparisons exact and avoid binary floating-point errors in Python and JavaScript. Calendar-date strings represent the input's meaning without timezone conversion.
- **Alternatives considered**: SQLite `REAL` values and JavaScript numbers are simpler but can introduce rounding error. Storing formatted monetary text makes exact SQL aggregation more complex.

### Fixed category vocabulary

- **Decision**: Use a fixed, documented category list: Housing, Utilities, Groceries, Transport, Health, Dining, Shopping, Entertainment, and Other. Store canonical category slugs and display their labels consistently. Reject unknown categories.
- **Rationale**: The specification excludes category creation/renaming. A fixed list keeps the interface and budget associations simple and testable.
- **Alternatives considered**: User-managed categories expand the feature and require category lifecycle rules, migration behavior, and handling of renamed/deleted categories.

### Expense and budget validation

- **Decision**: Validate required fields, category membership, positive EUR amount, exact date format and calendar validity, boolean necessity, and optional note type before persistence. Repeat essential invariants with SQLite `NOT NULL`, `CHECK`, and `UNIQUE` constraints. Enforce one budget per `(month, category)` and replace that budget when the user saves an updated limit. A monthly budget must be positive and use the same cents representation.
- **Rationale**: Request validation provides actionable errors; database constraints protect stored consistency if another code path is introduced. A unique budget key matches the user-visible concept of one category limit per month.
- **Alternatives considered**: Relying only on browser validation or API validation leaves other persistence paths unprotected. Allowing duplicate budgets creates ambiguous progress values.

### Browser interface and chart

- **Decision**: Serve one HTML page and static plain JavaScript/CSS from FastAPI. Use same-origin JSON requests for expense, summary, and budget actions. Render the monthly category chart as labeled horizontal bars with exact values and a text/table equivalent; use no charting library. Insert user-entered text as text, not HTML.
- **Rationale**: This satisfies the no-framework requirement and keeps the chart understandable without relying on color or a third-party service. The server remains authoritative for totals.
- **Alternatives considered**: A chart library adds a dependency for a fixed category chart. Canvas-only or color-only charts are harder to inspect and less accessible.

### Test strategy

- **Decision**: Use pytest and FastAPI `TestClient` with a fresh SQLite database under `tmp_path` per test. Cover API-to-database behavior, persistence across application recreation, validation failures, combined filters, calendar-month boundaries, summaries, and budget recalculation after edits/deletes. Add a small browser smoke check for the HTML/static interface as part of manual verification.
- **Rationale**: Integration tests verify the critical application boundary and keep tests isolated from real user data. Parametrized invalid values make validation behavior reproducible.
- **Alternatives considered**: Unit-only tests can miss route/database integration defects. A full browser automation suite adds setup and maintenance overhead for the initial implementation.

## Resolved Planning Assumptions

- The local application supports one user and one currency (EUR), without accounts, sharing, import/export, backup, or synchronization.
- The initial category labels are the fixed list above; adding categories is a later specification change.
- The application is optimized for normal personal use on one local machine, with up to 10,000 expense records as an initial planning test dataset. Common list, summary, and budget views should load within one second on the development machine for that dataset.
- Input and display use the decimal point as the EUR fractional separator; the interface displays EUR values with an explicit `EUR`/`€` marker. Locale-specific formatting is not required for the first version.
- No authentication is provided. Loopback binding, Host validation, same-origin writes, and restrictive static serving are part of the local-only boundary, not a substitute for operating-system account security.

## References

- [Python `sqlite3`](https://docs.python.org/3.15/library/sqlite3.html)
- [Python `decimal`](https://docs.python.org/3.15/library/decimal.html)
- [SQLite data types](https://www.sqlite.org/datatype3.html) and [table constraints](https://www.sqlite.org/lang_createtable.html)
- [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/) and [testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) and [XSS prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [W3C complex image guidance](https://www.w3.org/WAI/tutorials/images/complex/)
