from httpx import AsyncClient

sample_data = {
  "title": "Weekly groceries",
  "amount": 1,
  "date": "2026-09-11",
}

async def test_create_expense_success(client: AsyncClient, auth_headers: dict, test_category_id):
    create_data = {**sample_data, "category_id": test_category_id}
    response = await client.post("/api/v1/expenses", json=create_data, headers=auth_headers)

    assert response.status_code == 201
    assert "id" in response.json()["data"]


async def test_create_expense_invalid_category(client: AsyncClient, auth_headers: dict):
    create_data = {**sample_data, "category_id": "9819f4f7-7dcc-495d-a8d7-229d76a35a0e"}
    response = await client.post("/api/v1/expenses", json=create_data, headers=auth_headers)

    assert response.status_code == 404


async def test_get_expenses_list(client: AsyncClient, auth_headers: dict, test_category_id):
    create_data = {**sample_data, "category_id": test_category_id}
    await client.post("/api/v1/expenses", json=create_data, headers=auth_headers)
    await client.post("/api/v1/expenses", json=create_data, headers=auth_headers)

    response = await client.get("/api/v1/expenses", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


async def test_get_single_expense(client: AsyncClient, auth_headers: dict, test_category_id):
    create_data = {**sample_data, "category_id": test_category_id}
    create_res = await client.post("/api/v1/expenses", json=create_data, headers=auth_headers)
    expense_id = create_res.json()["data"]["id"]

    response = await client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers)

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["title"] == create_data["title"]
    assert res_data["data"]["amount"] == create_data["amount"]
    assert res_data["data"]["date"] == create_data["date"]


async def test_update_expense(client: AsyncClient, auth_headers: dict, test_category_id):
    create_data = {**sample_data, "category_id": test_category_id}
    create_res = await client.post("/api/v1/expenses", json=create_data, headers=auth_headers)
    expense_id = create_res.json()["data"]["id"]

    response = await client.patch(f"/api/v1/expenses/{expense_id}", headers=auth_headers, json={"amount": 100})

    assert response.status_code == 200
    assert response.json()["data"]["amount"] == 100
    assert response.json()["data"]["title"] == create_data["title"]

async def test_delete_expense(client: AsyncClient, auth_headers: dict, test_category_id):
    create_data = {**sample_data, "category_id": test_category_id}
    create_res = await client.post("/api/v1/expenses", json=create_data, headers=auth_headers)
    expense_id = create_res.json()["data"]["id"]

    delete_response = await client.delete(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    get_response = await client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
    assert get_response.status_code == 404


async def test_expense_user_isolation(client: AsyncClient, auth_headers: dict, test_category_id):
    create_data = {**sample_data, "category_id": test_category_id}
    create_res = await client.post("/api/v1/expenses", json=create_data, headers=auth_headers)
    user1_expense_id = create_res.json()["data"]["id"]

    # User 2 register & logs in
    await client.post("/api/v1/auth/register", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "Password123!",
    })
    user2_login_response = await client.post("/api/v1/auth/login", data={"username": "user2", "password": "Password123!"})
    user2_token = user2_login_response.json()["access_token"]
    user2_header = {"Authorization": f"Bearer {user2_token}"}

    user2_get_response = await client.get(f"/api/v1/expenses/{user1_expense_id}", headers=user2_header)

    assert user2_get_response.status_code == 404

    user2_delete_response = await client.delete(f"/api/v1/expenses/{user1_expense_id}", headers=user2_header)

    assert user2_delete_response.status_code == 404


async def test_filter_expenses_multi_param(client: AsyncClient, auth_headers: dict, test_category_id):
    await client.post("/api/v1/expenses", json={"title": "Transport", "amount": 500, "date": "2026-08-13", "category_id": test_category_id}, headers=auth_headers)

    await client.post("/api/v1/expenses", json={"title": "Food", "amount": 120, "date": "2026-08-24", "category_id": test_category_id}, headers=auth_headers)

    await client.post("/api/v1/expenses", json={"title": "Games", "amount": 80, "date": "2026-09-15", "category_id": test_category_id}, headers=auth_headers)

    query_params = {
        "start_date": "2026-08-01",
        "end_date": "2026-08-31",
        "min_amount": 100,
        "max_amount": 600,
        "sort_by": "amount",
        "order": "desc",
        "page": 1,
        "page_size": 10
    }

    response = await client.get("/api/v1/expenses?min_amount=100", params=query_params, headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["data"]

    assert len(items) == 2
    assert items[0]["amount"] == 500
    assert items[1]["amount"] == 120



async def test_expense_summary(client: AsyncClient, auth_headers: dict, test_category_id):
    create_data1 = {
        "title": "Transport",
        "amount": 500,
        "date": "2026-08-13",
        "category_id": test_category_id
    }
    create_data2 = {
        "title": "food",
        "amount": 50,
        "date": "2026-09-10",
        "category_id": test_category_id
    }
    await client.post("/api/v1/expenses", json=create_data1, headers=auth_headers)
    await client.post("/api/v1/expenses", json=create_data2, headers=auth_headers)

    response = await client.get("/api/v1/expenses/summary", params={"include_ai": False}, headers=auth_headers)

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["total_spending"] == 550
    assert len(res_data["data"]["by_category"]) == 1
    assert res_data["data"]["ai_insight"] is None