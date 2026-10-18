from fastapi.testclient import TestClient

from app import create_app


def client_for(tmp_path):
    return TestClient(create_app(tmp_path / "test.sqlite3"))


def test_expense_crud_and_monthly_summary(tmp_path):
    with client_for(tmp_path) as client:
        created = client.post(
            "/api/expenses",
            json={
                "amount": 42.5,
                "date": "2026-10-03",
                "category": "Groceries",
                "necessity": True,
                "note": "Weekly shop",
            },
        )
        assert created.status_code == 201
        expense_id = created.json()["id"]

        updated = client.put(
            f"/api/expenses/{expense_id}",
            json={
                "amount": 50,
                "date": "2026-10-04",
                "category": "Food",
                "necessity": False,
                "note": None,
            },
        )
        assert updated.status_code == 200

        summary = client.get("/api/summary", params={"month": "2026-10"}).json()
        assert summary["total"] == 50
        assert summary["categories"][0]["category"] == "Food"
        assert summary["categories"][0]["necessities"] == 0

        removed = client.delete(f"/api/expenses/{expense_id}")
        assert removed.status_code == 204
        assert client.get("/api/expenses").json() == []


def test_filters_budgets_and_month_isolation(tmp_path):
    with client_for(tmp_path) as client:
        client.post(
            "/api/expenses",
            json={
                "amount": 15.25,
                "date": "2026-10-10",
                "category": "Transit",
                "necessity": True,
                "note": "Train pass",
            },
        )
        client.post(
            "/api/expenses",
            json={
                "amount": 9,
                "date": "2026-09-10",
                "category": "Transit",
                "necessity": False,
                "note": "Taxi",
            },
        )

        assert len(client.get("/api/expenses", params={"month": "2026-10", "necessity": True}).json()) == 1
        assert len(client.get("/api/expenses", params={"search": "train"}).json()) == 1
        assert len(client.get("/api/expenses", params={"start_date": "2026-10-10", "end_date": "2026-10-10"}).json()) == 1
        assert len(client.get("/api/expenses", params={"start_date": "2026-10-11"}).json()) == 0
        assert client.get(
            "/api/expenses", params={"start_date": "2026-10-11", "end_date": "2026-10-09"}
        ).status_code == 422
        assert client.get("/api/summary", params={"month": "2026-10"}).json()["remaining"] == 0

        budget = client.put(
            "/api/budgets",
            json={"month": "2026-10", "category": "Transit", "amount": 100},
        )
        assert budget.status_code == 200
        summary = client.get("/api/summary", params={"month": "2026-10"}).json()
        assert summary["budget"] == 100
        assert summary["remaining"] == 84.75
        assert summary["categories"][0]["has_budget"] is True
        assert client.get("/api/summary", params={"month": "2026-09"}).json()["budget"] == 0

        zero_budget = client.put(
            "/api/budgets",
            json={"month": "2026-10", "category": "Transit", "amount": 0},
        )
        assert zero_budget.status_code == 200
        assert zero_budget.json()["amount"] == 0
        assert client.get("/api/budgets", params={"month": "2026-10"}).json() == [
            {"month": "2026-10", "category": "Transit", "amount": 0}
        ]
        zero_summary = client.get("/api/summary", params={"month": "2026-10"}).json()
        assert zero_summary["budget"] == 0
        assert zero_summary["remaining"] == -15.25
        assert zero_summary["categories"][0]["has_budget"] is True


def test_rejects_invalid_month_and_missing_expense(tmp_path):
    with client_for(tmp_path) as client:
        assert client.get("/api/summary", params={"month": "October"}).status_code == 422
        assert client.delete("/api/expenses/999").status_code == 404