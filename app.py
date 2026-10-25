from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "expenses.db"
STATIC_DIR = BASE_DIR / "static"

CATEGORY_ORDER = [
    "housing",
    "utilities",
    "groceries",
    "transport",
    "health",
    "dining",
    "shopping",
    "entertainment",
    "other",
]
CATEGORY_LABELS = {
    "housing": "Housing",
    "utilities": "Utilities",
    "groceries": "Groceries",
    "transport": "Transport",
    "health": "Health",
    "dining": "Dining",
    "shopping": "Shopping",
    "entertainment": "Entertainment",
    "other": "Other",
}
CATEGORY_SET = set(CATEGORY_ORDER)


def _valid_db_path(db_path: str | Path | None) -> Path:
    if db_path is None:
        return DEFAULT_DB_PATH
    return Path(db_path).resolve()


def _is_loopback_host(host_value: str | None) -> bool:
    if not host_value:
        return False
    host = host_value.strip().lower().rstrip(".")
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]
    if host in {"localhost", "127.0.0.1", "::1", "testserver"}:
        return True
    if host.startswith("localhost:") or host.startswith("testserver:"):
        return True
    if host.startswith("127."):
        return True
    if host.startswith("[::1]"):
        return True
    if host.startswith("::1:"):
        return True
    return False


def _validate_amount(value: Any) -> int:
    if not isinstance(value, str):
        raise ValueError("Amount must be a decimal string.")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Amount must be a valid decimal number.") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be a positive finite decimal value.")
    if abs(amount.as_tuple().exponent) > 2:
        raise ValueError("Amount may have at most two decimal places.")
    return int((amount * 100).to_integral_value())


def _validate_iso_date(value: Any) -> str:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError("Date must be a valid ISO date string in YYYY-MM-DD format.")
    try:
        year, month, day = value.split("-")
        if not (year.isdigit() and month.isdigit() and day.isdigit()):
            raise ValueError
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Date must be a real calendar date in YYYY-MM-DD format.") from exc
    return value


def _validate_month(value: Any) -> str:
    if not isinstance(value, str) or len(value) != 7:
        raise ValueError("Month must be in YYYY-MM format.")
    try:
        year, month = value.split("-")
        if not (year.isdigit() and month.isdigit()):
            raise ValueError
        date(int(year), int(month), 1)
    except ValueError as exc:
        raise ValueError("Month must be a valid calendar month.") from exc
    return value


def _month_bounds(month: str) -> tuple[str, str]:
    year, month_number = (int(part) for part in month.split("-"))
    start_date = f"{month}-01"
    if month_number == 12:
        end_date = f"{year + 1:04d}-01-01"
    else:
        end_date = f"{year:04d}-{month_number + 1:02d}-01"
    return start_date, end_date


def _validate_note(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Note must be text or null.")
    return value


def _validate_necessity(value: Any) -> bool:
    if value is True or value is False:
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    raise ValueError("Necessity must be true or false.")


def _validate_category(value: Any) -> str:
    if value not in CATEGORY_SET:
        raise ValueError(f"Category must be one of: {', '.join(CATEGORY_ORDER)}")
    return value


def _to_expense_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "amount": _cents_to_eur(row["amount_cents"]),
        "currency": "EUR",
        "date": row["spent_on"],
        "category": row["category"],
        "category_label": CATEGORY_LABELS[row["category"]],
        "is_necessity": bool(row["is_necessity"]),
        "note": row["note"],
    }


def _cents_to_eur(cents: int) -> str:
    return format(Decimal(cents) / Decimal("100"), ".2f")


def _to_budget_payload(row: sqlite3.Row) -> dict[str, Any]:
    limit_cents = row["amount_cents"]
    spent_cents = row["spent_cents"]
    return {
        "month": row["month"],
        "category": row["category"],
        "category_label": CATEGORY_LABELS[row["category"]],
        "limit": _cents_to_eur(limit_cents),
        "spent": _cents_to_eur(spent_cents),
        "remaining": _cents_to_eur(max(limit_cents - spent_cents, 0)),
        "overage": _cents_to_eur(max(spent_cents - limit_cents, 0)),
        "progress_percent": float(Decimal(spent_cents) * 100 / Decimal(limit_cents)),
        "currency": "EUR",
    }


async def _read_request_payload(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Request body must be valid JSON.") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="Request body must be a JSON object.")
    return payload


def init_db(db_path: str | Path) -> Path:
    path = _valid_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
                spent_on TEXT NOT NULL,
                category TEXT NOT NULL,
                is_necessity INTEGER NOT NULL CHECK (is_necessity IN (0, 1)),
                note TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_budgets (
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
                PRIMARY KEY (month, category)
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_expenses_month_category ON expenses (spent_on, category)"
        )
    return path


def _database_connection(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(_valid_db_path(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_app(db_path: str | Path | None = None) -> FastAPI:
    app = FastAPI(title="Expense Tracker")
    resolved_db_path = _valid_db_path(db_path)
    app.state.db_path = str(resolved_db_path)
    app.state.categories = CATEGORY_ORDER
    init_db(resolved_db_path)

    @app.middleware("http")
    async def enforce_host_and_db(request: Request, call_next):
        host = request.headers.get("host")
        if host is None or not _is_loopback_host(host):
            return JSONResponse(status_code=403, content={"detail": "Host must be loopback only."})

        if request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if not origin:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Origin header required for mutation requests."},
                )
            origin_parts = urlsplit(origin)
            if origin_parts.scheme not in {"http", "https"}:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Origin must match the current host."},
                )
            request_parts = urlsplit(str(request.base_url))
            try:
                origin_port = origin_parts.port or (443 if origin_parts.scheme == "https" else 80)
                request_port = request_parts.port or (443 if request_parts.scheme == "https" else 80)
            except ValueError:
                origin_port = None
                request_port = -1
            same_origin = (
                origin_parts.username is None
                and origin_parts.password is None
                and origin_parts.scheme == request_parts.scheme
                and (origin_parts.hostname or "").lower() == (request_parts.hostname or "").lower()
                and origin_port == request_port
                and _is_loopback_host(origin_parts.hostname)
            )
            if not same_origin:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Origin must match the current host."},
                )

        conn = _database_connection(app.state.db_path)
        request.state.db = conn
        try:
            return await call_next(request)
        finally:
            conn.close()

    @app.get("/")
    async def serve_index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/categories")
    async def get_categories() -> list[dict[str, str]]:
        return [{"id": category, "label": CATEGORY_LABELS[category]} for category in CATEGORY_ORDER]

    @app.get("/api/summary")
    async def get_monthly_summary(request: Request):
        month = request.query_params.get("month")
        if month is None:
            raise HTTPException(status_code=422, detail="Field 'month' is required.")
        try:
            month = _validate_month(month)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        start_date, end_date = _month_bounds(month)

        rows = request.state.db.execute(
            """
            SELECT category, SUM(amount_cents) AS total_cents
            FROM expenses
            WHERE spent_on >= ? AND spent_on < ?
            GROUP BY category
            """,
            (start_date, end_date),
        ).fetchall()
        totals_by_category = {row["category"]: row["total_cents"] for row in rows}
        category_totals = [
            {
                "id": category,
                "label": CATEGORY_LABELS[category],
                "total": _cents_to_eur(totals_by_category.get(category, 0)),
            }
            for category in CATEGORY_ORDER
        ]
        total_cents = sum(totals_by_category.values())
        return {
            "month": month,
            "currency": "EUR",
            "total": _cents_to_eur(total_cents),
            "categories": category_totals,
        }

    @app.get("/api/budgets")
    async def get_budgets(request: Request):
        month = request.query_params.get("month")
        if month is None:
            raise HTTPException(status_code=422, detail="Field 'month' is required.")
        try:
            month = _validate_month(month)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        start_date, end_date = _month_bounds(month)
        rows = request.state.db.execute(
            """
            SELECT b.month, b.category, b.amount_cents,
                   COALESCE(SUM(e.amount_cents), 0) AS spent_cents
            FROM monthly_budgets AS b
            LEFT JOIN expenses AS e
              ON e.category = b.category
             AND e.spent_on >= ?
             AND e.spent_on < ?
            WHERE b.month = ?
            GROUP BY b.month, b.category, b.amount_cents
            ORDER BY b.category
            """,
            (start_date, end_date, month),
        ).fetchall()
        return [_to_budget_payload(row) for row in rows]

    @app.put("/api/budgets/{month}/{category}")
    async def put_budget(request: Request, month: str, category: str):
        try:
            month = _validate_month(month)
            category = _validate_category(category)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        payload = await _read_request_payload(request)
        try:
            amount_cents = _validate_amount(payload.get("limit"))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        try:
            request.state.db.execute(
                """
                INSERT INTO monthly_budgets (month, category, amount_cents)
                VALUES (?, ?, ?)
                ON CONFLICT (month, category)
                DO UPDATE SET amount_cents = excluded.amount_cents
                """,
                (month, category, amount_cents),
            )
            request.state.db.commit()
        except sqlite3.IntegrityError as exc:
            request.state.db.rollback()
            raise HTTPException(status_code=422, detail="Budget could not be saved.") from exc

        start_date, end_date = _month_bounds(month)
        row = request.state.db.execute(
            """
            SELECT b.month, b.category, b.amount_cents,
                   COALESCE(SUM(e.amount_cents), 0) AS spent_cents
            FROM monthly_budgets AS b
            LEFT JOIN expenses AS e
              ON e.category = b.category
             AND e.spent_on >= ?
             AND e.spent_on < ?
            WHERE b.month = ? AND b.category = ?
            GROUP BY b.month, b.category, b.amount_cents
            """,
            (start_date, end_date, month, category),
        ).fetchone()
        return _to_budget_payload(row)

    @app.get("/api/expenses")
    async def list_expenses(request: Request):
        query = request.query_params
        sql = "SELECT id, amount_cents, spent_on, category, is_necessity, note FROM expenses WHERE 1=1"
        params: list[Any] = []

        start = query.get("from")
        end = query.get("to")
        if start is not None:
            try:
                start = _validate_iso_date(start)
            except ValueError as exc:
                raise HTTPException(422, detail=str(exc)) from exc
            sql += " AND spent_on >= ?"
            params.append(start)
        if end is not None:
            try:
                end = _validate_iso_date(end)
            except ValueError as exc:
                raise HTTPException(422, detail=str(exc)) from exc
            sql += " AND spent_on <= ?"
            params.append(end)
        if start and end and start > end:
            raise HTTPException(422, detail="The start date must be on or before the end date.")

        category = query.get("category")
        if category is not None:
            try:
                category = _validate_category(category)
            except ValueError as exc:
                raise HTTPException(422, detail=str(exc)) from exc
            sql += " AND category = ?"
            params.append(category)

        necessity = query.get("necessity")
        if necessity is not None:
            if necessity not in {"true", "false"}:
                raise HTTPException(422, detail="Necessity filter must be true or false.")
            sql += " AND is_necessity = ?"
            params.append(1 if necessity == "true" else 0)

        sql += " ORDER BY spent_on DESC, id DESC"
        rows = request.state.db.execute(sql, params).fetchall()
        return [_to_expense_payload(row) for row in rows]

    @app.post("/api/expenses")
    async def create_expense(request: Request):
        payload = await _read_request_payload(request)
        for field in ("amount", "date", "category", "is_necessity"):
            if field not in payload:
                raise HTTPException(422, detail=f"Field '{field}' is required.")

        try:
            amount_cents = _validate_amount(payload["amount"])
            spent_on = _validate_iso_date(payload["date"])
            category = _validate_category(payload["category"])
            necessity = _validate_necessity(payload["is_necessity"])
            note = _validate_note(payload.get("note"))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        try:
            request.state.db.execute(
                """
                INSERT INTO expenses (amount_cents, spent_on, category, is_necessity, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (amount_cents, spent_on, category, int(necessity), note),
            )
            request.state.db.commit()
            expense_id = request.state.db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        except sqlite3.IntegrityError as exc:
            request.state.db.rollback()
            raise HTTPException(status_code=422, detail="Expense could not be saved.") from exc

        row = request.state.db.execute(
            "SELECT id, amount_cents, spent_on, category, is_necessity, note FROM expenses WHERE id = ?",
            (expense_id,),
        ).fetchone()
        response = _to_expense_payload(row)
        return JSONResponse(status_code=201, content=response)

    @app.put("/api/expenses/{expense_id}")
    async def update_expense(request: Request, expense_id: int):
        payload = await _read_request_payload(request)
        row = request.state.db.execute(
            "SELECT id FROM expenses WHERE id = ?",
            (expense_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Expense not found.")

        for field in ("amount", "date", "category", "is_necessity"):
            if field not in payload:
                raise HTTPException(422, detail=f"Field '{field}' is required.")

        try:
            amount_cents = _validate_amount(payload["amount"])
            spent_on = _validate_iso_date(payload["date"])
            category = _validate_category(payload["category"])
            necessity = _validate_necessity(payload["is_necessity"])
            note = _validate_note(payload.get("note"))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        try:
            request.state.db.execute(
                """
                UPDATE expenses
                SET amount_cents = ?, spent_on = ?, category = ?, is_necessity = ?, note = ?
                WHERE id = ?
                """,
                (amount_cents, spent_on, category, int(necessity), note, expense_id),
            )
            request.state.db.commit()
        except sqlite3.IntegrityError as exc:
            request.state.db.rollback()
            raise HTTPException(status_code=422, detail="Expense could not be updated.") from exc

        row = request.state.db.execute(
            "SELECT id, amount_cents, spent_on, category, is_necessity, note FROM expenses WHERE id = ?",
            (expense_id,),
        ).fetchone()
        return _to_expense_payload(row)

    @app.delete("/api/expenses/{expense_id}")
    async def delete_expense(request: Request, expense_id: int) -> Response:
        row = request.state.db.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Expense not found.")
        request.state.db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        request.state.db.commit()
        return Response(status_code=204)

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    return app


app = create_app(DEFAULT_DB_PATH)
