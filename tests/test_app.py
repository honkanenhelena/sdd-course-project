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
