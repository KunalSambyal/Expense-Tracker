from httpx import AsyncClient

async def test_create_category_success(client: AsyncClient, auth_headers: dict):
    response = await client.post("/api/v1/categories", json={"name": "food"}, headers=auth_headers)
    assert response.status_code == 201
    res_data = response.json()
    assert "id" in res_data["data"]


async def test_create_duplicate_category(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/categories", json={"name": "food"}, headers=auth_headers)
    response = await client.post("/api/v1/categories", json={"name": "food"}, headers=auth_headers)
    assert response.status_code == 400


async def test_get_categories(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/categories", json={"name": "food"}, headers=auth_headers)
    await client.post("/api/v1/categories", json={"name": "transport"}, headers=auth_headers)
    response = await client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data["data"]) == 2


async def test_delete_category(client: AsyncClient, auth_headers: dict):
    create_response = await client.post("/api/v1/categories", json={"name": "food"}, headers=auth_headers)
    category_id = (create_response.json())["data"]["id"]

    delete_response = await client.delete(f"/api/v1/categories/{category_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    get_response = await client.get("/api/v1/categories", headers=auth_headers)
    assert len((get_response.json())["data"]) == 0


async def test_category_user_isolation(client: AsyncClient, auth_headers: dict):
    create_cat_response = await client.post("/api/v1/categories", json={"name": "user1_seceret_cat"}, headers=auth_headers)
    user1_category_id = (create_cat_response.json())["data"]["id"]

    await client.post("/api/v1/auth/register", json={
        "username": "user2", "email": "user2@example.com", "password": "Password123!"
    })
    user2_login_res = await client.post("/api/v1/auth/login", data={"username": "user2", "password": "Password123!"})
    user2_token = (user2_login_res.json())["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    user2_category_res = await client.get("/api/v1/categories", headers=user2_headers)
    assert len(user2_category_res.json()["data"]) == 0

    delete_res = await client.delete(f"/api/v1/categories/{user1_category_id}", headers=user2_headers)
    assert delete_res.status_code == 404
