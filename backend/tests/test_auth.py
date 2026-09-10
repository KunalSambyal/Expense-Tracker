from httpx import AsyncClient

async def test_register_success(client: AsyncClient):
    payload = {
        "username": "kunal67",
        "email": "kunal@example.com",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["username"] == "kunal67"
    assert res_data["data"]["email"] == "kunal@example.com"
    assert "id" in res_data["data"]


async def test_register_duplicate(client: AsyncClient):
    payload = {
        "username": "kunal67",
        "email": "kunal@example.com",
        "password": "Password123!"
    }

    await client.post("/api/v1/auth/register", json=payload)

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["success"] is False


async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "kunal67",
        "email": "kunal@example.com",
        "password": "Password123!"
    })

    login_data = {
        "username": "kunal67",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 200
    res_data = response.json()
    assert "access_token" in res_data
    assert res_data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "kunal69",
        "email": "kunal@example.com",
        "password": "Password123!"
    })

    login_data = {
        "username": "kunal69",
        "password": "Password321!"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 401
    res_data = response.json()
    assert res_data["message"] == "Incorrect username or password"


async def test_login_user_not_found(client: AsyncClient):
    login_data = {
        "username": "kunal67",
        "password": "Password321!"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 401
    res_data = response.json()
    assert res_data["message"] == "Incorrect username or password"


async def test_get_me_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
            "username": "kunal69",
            "email": "kunal@example.com",
            "password": "Password123!"
        })

    login_data = {
        "username": "kunal69",
        "password": "Password123!"
    }

    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    res_data = response.json()
    token = res_data["access_token"]

    get_response = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})

    assert get_response.status_code == 200
    assert get_response.json()["data"]["username"] == "kunal69"


async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401