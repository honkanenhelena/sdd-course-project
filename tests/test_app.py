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
