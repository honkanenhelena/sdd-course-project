from contextlib import asynccontextmanager, contextmanager
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import os
from pathlib import Path
import re
import sqlite3
from typing import Iterator

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class ExpenseInput(BaseModel):
    amount: float = Field(gt=0, le=10_000_000)
    date: date
    category: str = Field(min_length=1, max_length=60)
    necessity: bool
    note: str | None = Field(default=None, max_length=500)


class BudgetInput(BaseModel):
    month: str
    category: str = Field(min_length=1, max_length=60)
    amount: float = Field(ge=0, le=10_000_000)


def _month(value: str) -> str:
    if not MONTH_PATTERN.fullmatch(value):
        raise HTTPException(status_code=422, detail="Month must use YYYY-MM format")
    return value


def _cents(value: float) -> int:
    try:
        result = int((Decimal(str(value)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except InvalidOperation as error:
        raise HTTPException(status_code=422, detail="Amount is invalid") from error
    if result <= 0:
        raise HTTPException(status_code=422, detail="Amount must be at least 0.01")
    return result


def _clean_category(value: str) -> str:
    category = value.strip()
    if not category:
        raise HTTPException(status_code=422, detail="Category cannot be empty")
    return category


def create_app(database_path: str | Path | None = None) -> FastAPI:
    db_path = Path(database_path or os.getenv("DATABASE_PATH", BASE_DIR / "expenses.db"))

    @contextmanager
    def connection() -> Iterator[sqlite3.Connection]:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def initialize_database() -> None:
        with connection() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
                    spent_on TEXT NOT NULL,
                    category TEXT NOT NULL,
                    necessity INTEGER NOT NULL CHECK (necessity IN (0, 1)),
                    note TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_expenses_spent_on
                    ON expenses(spent_on);
                CREATE TABLE IF NOT EXISTS budgets (
                    month TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
                    PRIMARY KEY (month, category)
                );
                """
            )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        initialize_database()
        yield

    app = FastAPI(title="Pocket Ledger", lifespan=lifespan)
    app.state.connection = connection

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/api/expenses")
    def list_expenses(
        month: str | None = None,
        category: str | None = None,
        necessity: bool | None = None,
        search: str | None = Query(default=None, max_length=100),
    ) -> list[dict]:
        clauses: list[str] = []
        values: list[object] = []
        if month:
            clauses.append("substr(spent_on, 1, 7) = ?")
            values.append(_month(month))
        if category:
            clauses.append("category = ?")
            values.append(category)
        if necessity is not None:
            clauses.append("necessity = ?")
            values.append(int(necessity))
        if search:
            clauses.append("lower(coalesce(note, '') || ' ' || category) LIKE ?")
            values.append(f"%{search.strip().lower()}%")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with connection() as db:
            rows = db.execute(
                f"SELECT id, amount_cents, spent_on, category, necessity, note "
                f"FROM expenses {where} ORDER BY spent_on DESC, id DESC",
                values,
            ).fetchall()
        return [
            {
                "id": row["id"],
                "amount": row["amount_cents"] / 100,
                "date": row["spent_on"],
                "category": row["category"],
                "necessity": bool(row["necessity"]),
                "note": row["note"],
            }
            for row in rows
        ]

    @app.post("/api/expenses", status_code=201)
    def add_expense(expense: ExpenseInput) -> dict:
        category = _clean_category(expense.category)
        with connection() as db:
            cursor = db.execute(
                "INSERT INTO expenses (amount_cents, spent_on, category, necessity, note) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    _cents(expense.amount),
                    expense.date.isoformat(),
                    category,
                    int(expense.necessity),
                    expense.note.strip() or None if expense.note else None,
                ),
            )
            expense_id = cursor.lastrowid
        return {"id": expense_id, **expense.model_dump(), "category": category}

    @app.put("/api/expenses/{expense_id}")
    def edit_expense(expense_id: int, expense: ExpenseInput) -> dict:
        category = _clean_category(expense.category)
        with connection() as db:
            cursor = db.execute(
                "UPDATE expenses SET amount_cents = ?, spent_on = ?, category = ?, "
                "necessity = ?, note = ? WHERE id = ?",
                (
                    _cents(expense.amount),
                    expense.date.isoformat(),
                    category,
                    int(expense.necessity),
                    expense.note.strip() or None if expense.note else None,
                    expense_id,
                ),
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Expense not found")
        return {"id": expense_id, **expense.model_dump(), "category": category}

    @app.delete("/api/expenses/{expense_id}", status_code=204)
    def remove_expense(expense_id: int) -> Response:
        with connection() as db:
            cursor = db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Expense not found")
        return Response(status_code=204)

    @app.get("/api/summary")
    def monthly_summary(month: str = Query(...)) -> dict:
        selected_month = _month(month)
        with connection() as db:
            spend_rows = db.execute(
                "SELECT category, SUM(amount_cents) AS total_cents, "
                "SUM(CASE WHEN necessity = 1 THEN amount_cents ELSE 0 END) AS needs_cents, "
                "COUNT(*) AS count FROM expenses "
                "WHERE substr(spent_on, 1, 7) = ? GROUP BY category",
                (selected_month,),
            ).fetchall()
            budget_rows = db.execute(
                "SELECT category, amount_cents FROM budgets WHERE month = ?",
                (selected_month,),
            ).fetchall()
        spending = {row["category"]: row for row in spend_rows}
        budgets = {row["category"]: row["amount_cents"] for row in budget_rows}
        budgeted_spending_cents = sum(
            spending[category]["total_cents"] for category in budgets if category in spending
        )
        categories = []
        for category in sorted(spending.keys() | budgets.keys()):
            spent_cents = spending[category]["total_cents"] if category in spending else 0
            budget_cents = budgets.get(category, 0)
            categories.append(
                {
                    "category": category,
                    "spent": spent_cents / 100,
                    "necessities": (spending[category]["needs_cents"] if category in spending else 0) / 100,
                    "count": spending[category]["count"] if category in spending else 0,
                    "budget": budget_cents / 100,
                    "remaining": (budget_cents - spent_cents) / 100,
                }
            )
        total_cents = sum(row["total_cents"] for row in spend_rows)
        total_budget_cents = sum(budgets.values())
        return {
            "month": selected_month,
            "total": total_cents / 100,
            "budget": total_budget_cents / 100,
            "remaining": (total_budget_cents - budgeted_spending_cents) / 100,
            "expense_count": sum(row["count"] for row in spend_rows),
            "categories": categories,
        }

    @app.get("/api/budgets")
    def list_budgets(month: str = Query(...)) -> list[dict]:
        selected_month = _month(month)
        with connection() as db:
            rows = db.execute(
                "SELECT category, amount_cents FROM budgets WHERE month = ? ORDER BY category",
                (selected_month,),
            ).fetchall()
        return [
            {"month": selected_month, "category": row["category"], "amount": row["amount_cents"] / 100}
            for row in rows
        ]

    @app.put("/api/budgets")
    def set_budget(budget: BudgetInput) -> dict:
        selected_month = _month(budget.month)
        category = _clean_category(budget.category)
        amount_cents = int(
            (Decimal(str(budget.amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
        with connection() as db:
            if amount_cents == 0:
                db.execute(
                    "DELETE FROM budgets WHERE month = ? AND category = ?",
                    (selected_month, category),
                )
            else:
                db.execute(
                    "INSERT INTO budgets (month, category, amount_cents) VALUES (?, ?, ?) "
                    "ON CONFLICT(month, category) DO UPDATE SET amount_cents = excluded.amount_cents",
                    (selected_month, category, amount_cents),
                )
        return {"month": selected_month, "category": category, "amount": amount_cents / 100}

    @app.delete("/api/budgets", status_code=204)
    def remove_budget(month: str, category: str) -> Response:
        selected_month = _month(month)
        with connection() as db:
            db.execute(
                "DELETE FROM budgets WHERE month = ? AND category = ?",
                (selected_month, category),
            )
        return Response(status_code=204)

    return app


app = create_app()