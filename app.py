from __future__ import annotations

import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
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
    if host in {"localhost", "127.0.0.1", "::1"}:
        return True
    if host.startswith("127."):
        parts = host.split(".")
        return len(parts) == 4 and all(part.isdigit() for part in parts)
    if ":" in host:
        host_part = host.rsplit(":", 1)[0]
        return host_part in {"[::1]", "::1", "127.0.0.1"}
    return False


def _validate_amount(value: Any) -> int:
    if not isinstance(value, str):
        raise ValueError("Amount must be a decimal string.")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:  # pragma: no cover - converted at API boundary
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
        date_obj = sqlite3.connect(":memory:").execute(
            "SELECT date(?)",
            (value,),
        ).fetchone()[0]
    except Exception as exc:  # pragma: no cover - database validation keeps this safe
        raise ValueError("Date must be a real calendar date in YYYY-MM-DD format.") from exc
    return str(date_obj)


def _validate_month(value: Any) -> str:
    if not isinstance(value, str) or len(value) != 7:
        raise ValueError("Month must be in YYYY-MM format.")
    year, month = value.split("-")
    if not (year.isdigit() and month.isdigit()):
        raise ValueError("Month must be in YYYY-MM format.")
    month_num = int(month)
    if month_num < 1 or month_num > 12:
        raise ValueError("Month must be a valid calendar month.")
    return value


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


CATEGORY_SET = set(CATEGORY_ORDER)


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
            if origin_parts.netloc.lower() != host.lower():
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

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app


app = create_app(DEFAULT_DB_PATH)
