import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import create_app


@pytest.fixture()
def client_fixture(tmp_path):
    db_path = tmp_path / "expenses.db"
    app = create_app(db_path)
    with TestClient(app) as client:
        yield client, db_path


def test_app_creates_required_database_tables(client_fixture):
    client, db_path = client_fixture
    del client

    with sqlite3.connect(db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()

    table_names = {table[0] for table in tables}
    assert {"expenses", "monthly_budgets"}.issubset(table_names)


def test_app_rejects_non_loopback_host(tmp_path):
    app = create_app(tmp_path / "expenses.db")
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        response = client.get("/", headers={"host": "example.com"})

    assert response.status_code in {400, 403}


def test_get_categories_returns_fixed_order(client_fixture):
    client, _ = client_fixture

    response = client.get("/api/categories")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "housing", "label": "Housing"},
        {"id": "utilities", "label": "Utilities"},
        {"id": "groceries", "label": "Groceries"},
        {"id": "transport", "label": "Transport"},
        {"id": "health", "label": "Health"},
        {"id": "dining", "label": "Dining"},
        {"id": "shopping", "label": "Shopping"},
        {"id": "entertainment", "label": "Entertainment"},
        {"id": "other", "label": "Other"},
    ]


def test_expense_crud_and_validation(client_fixture):
    client, _ = client_fixture
    headers = {"origin": "http://127.0.0.1:8000"}

    create_payload = {
        "amount": "12.34",
        "date": "2026-10-22",
        "category": "groceries",
        "is_necessity": True,
        "note": "Weekly food shop",
    }
    create_response = client.post("/api/expenses", json=create_payload, headers=headers)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["amount"] == "12.34"
    assert created["category"] == "groceries"
    assert created["date"] == "2026-10-22"

    list_response = client.get("/api/expenses")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == created["id"]

    update_payload = {
        "amount": "18.50",
        "date": "2026-10-25",
        "category": "dining",
        "is_necessity": False,
        "note": "Dinner with friends",
    }
    update_response = client.put(
        f"/api/expenses/{created['id']}",
        json=update_payload,
        headers=headers,
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["amount"] == "18.50"
    assert updated["category"] == "dining"
    assert updated["note"] == "Dinner with friends"

    invalid_response = client.post(
        "/api/expenses",
        json={
            "amount": "0",
            "date": "2026-02-30",
            "category": "groceries",
            "is_necessity": True,
        },
        headers=headers,
    )
    assert invalid_response.status_code == 422

    persisted = client.get("/api/expenses")
    assert persisted.status_code == 200
    assert len(persisted.json()) == 1
    assert persisted.json()[0]["category"] == "dining"

    delete_response = client.delete(f"/api/expenses/{created['id']}", headers=headers)
    assert delete_response.status_code == 204

    after_delete = client.get("/api/expenses")
    assert after_delete.status_code == 200
    assert after_delete.json() == []


def test_expense_filters_are_inclusive_and_combinable(client_fixture):
    client, _ = client_fixture
    headers = {"origin": "http://127.0.0.1:8000"}
    expenses = [
        {"amount": "1.00", "date": "2026-10-01", "category": "groceries", "is_necessity": True},
        {"amount": "2.00", "date": "2026-10-31", "category": "groceries", "is_necessity": False},
        {"amount": "4.00", "date": "2026-11-01", "category": "groceries", "is_necessity": False},
        {"amount": "8.00", "date": "2026-10-15", "category": "dining", "is_necessity": False},
    ]
    for expense in expenses:
        assert client.post("/api/expenses", json=expense, headers=headers).status_code == 201

    boundary_response = client.get("/api/expenses?from=2026-10-01&to=2026-10-31")
    assert [item["date"] for item in boundary_response.json()] == [
        "2026-10-31",
        "2026-10-15",
        "2026-10-01",
    ]

    combined_response = client.get(
        "/api/expenses?from=2026-10-01&to=2026-10-31&category=groceries&necessity=false"
    )
    assert combined_response.status_code == 200
    assert [(item["date"], item["amount"]) for item in combined_response.json()] == [
        ("2026-10-31", "2.00")
    ]

    reversed_response = client.get("/api/expenses?from=2026-11-01&to=2026-10-31")
    assert reversed_response.status_code == 422
    assert reversed_response.json() == {
        "detail": "The start date must be on or before the end date."
    }


def test_monthly_summary_uses_month_boundaries_and_includes_zero_categories(client_fixture):
    client, _ = client_fixture
    headers = {"origin": "http://127.0.0.1:8000"}
    expenses = [
        {"amount": "3.45", "date": "2026-10-31", "category": "groceries", "is_necessity": True},
        {"amount": "6.00", "date": "2026-11-01", "category": "housing", "is_necessity": True},
    ]
    for expense in expenses:
        assert client.post("/api/expenses", json=expense, headers=headers).status_code == 201

    summary_response = client.get("/api/summary?month=2026-10")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["month"] == "2026-10"
    assert summary["currency"] == "EUR"
    assert summary["total"] == "3.45"
    assert [category["id"] for category in summary["categories"]] == [
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
    totals = {category["id"]: category["total"] for category in summary["categories"]}
    assert totals["groceries"] == "3.45"
    assert totals["housing"] == "0.00"
    assert all(total == "0.00" for category, total in totals.items() if category != "groceries")

    empty_response = client.get("/api/summary?month=2026-12")
    assert empty_response.status_code == 200
    assert empty_response.json()["total"] == "0.00"
    assert all(category["total"] == "0.00" for category in empty_response.json()["categories"])

    invalid_month_response = client.get("/api/summary?month=2026-13")
    assert invalid_month_response.status_code == 422


def test_budget_api_validates_month_category_and_positive_eur_amount(client_fixture):
    client, _ = client_fixture
    headers = {"origin": "http://127.0.0.1:8000"}

    assert client.get("/api/budgets").status_code == 422
    assert client.get("/api/budgets?month=2026-13").status_code == 422
    assert client.put(
        "/api/budgets/2026-13/groceries",
        json={"limit": "20.00"},
        headers=headers,
    ).status_code == 422
    assert client.put(
        "/api/budgets/2026-10/unknown",
        json={"limit": "20.00"},
        headers=headers,
    ).status_code == 422

    for limit in ("0", "-1.00", "1.001", "NaN", 20):
        response = client.put(
            "/api/budgets/2026-10/groceries",
            json={"limit": limit},
            headers=headers,
        )
        assert response.status_code == 422

    assert client.get("/api/budgets?month=2026-10").json() == []


def test_budget_upsert_and_progress_recalculate_after_expense_changes(client_fixture):
    client, _ = client_fixture
    headers = {"origin": "http://127.0.0.1:8000"}
    expense_response = client.post(
        "/api/expenses",
        json={
            "amount": "8.00",
            "date": "2026-10-15",
            "category": "groceries",
            "is_necessity": True,
        },
        headers=headers,
    )
    assert expense_response.status_code == 201
    expense_id = expense_response.json()["id"]

    budget_response = client.put(
        "/api/budgets/2026-10/groceries",
        json={"limit": "10.00"},
        headers=headers,
    )
    assert budget_response.status_code == 200
    assert budget_response.json() == {
        "month": "2026-10",
        "category": "groceries",
        "category_label": "Groceries",
        "limit": "10.00",
        "spent": "8.00",
        "remaining": "2.00",
        "overage": "0.00",
        "progress_percent": 80.0,
        "currency": "EUR",
    }
    assert client.get("/api/budgets?month=2026-10").json() == [budget_response.json()]

    update_headers = headers
    equal_response = client.put(
        f"/api/expenses/{expense_id}",
        json={
            "amount": "10.00",
            "date": "2026-10-15",
            "category": "groceries",
            "is_necessity": True,
        },
        headers=update_headers,
    )
    assert equal_response.status_code == 200
    equal_budget = client.get("/api/budgets?month=2026-10").json()[0]
    assert equal_budget["spent"] == "10.00"
    assert equal_budget["remaining"] == "0.00"
    assert equal_budget["overage"] == "0.00"
    assert equal_budget["progress_percent"] == 100.0

    over_limit_response = client.put(
        f"/api/expenses/{expense_id}",
        json={
            "amount": "12.00",
            "date": "2026-10-15",
            "category": "groceries",
            "is_necessity": True,
        },
        headers=headers,
    )
    assert over_limit_response.status_code == 200
    over_budget = client.get("/api/budgets?month=2026-10").json()[0]
    assert over_budget["spent"] == "12.00"
    assert over_budget["remaining"] == "0.00"
    assert over_budget["overage"] == "2.00"
    assert over_budget["progress_percent"] == 120.0

    delete_response = client.delete(f"/api/expenses/{expense_id}", headers=headers)
    assert delete_response.status_code == 204
    zero_spend = client.get("/api/budgets?month=2026-10").json()[0]
    assert zero_spend["spent"] == "0.00"
    assert zero_spend["remaining"] == "10.00"
    assert zero_spend["overage"] == "0.00"
    assert zero_spend["progress_percent"] == 0.0

    replaced = client.put(
        "/api/budgets/2026-10/groceries",
        json={"limit": "25.00"},
        headers=headers,
    )
    assert replaced.status_code == 200
    assert replaced.json()["limit"] == "25.00"
    assert len(client.get("/api/budgets?month=2026-10").json()) == 1

    zero_budget = client.put(
        "/api/budgets/2026-10/housing",
        json={"limit": "50.00"},
        headers=headers,
    )
    assert zero_budget.status_code == 200
    assert zero_budget.json()["spent"] == "0.00"
    assert zero_budget.json()["progress_percent"] == 0.0
