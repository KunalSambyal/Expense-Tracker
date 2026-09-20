import httpx
from config import API_BASE_URL

def _get_headers(token: str | None = None) -> dict:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# Auth Functions

def auth_register(username: str, email: str, password: str):
    payload = {"username": username, "email": email, "password": password}
    response = httpx.post(f"{API_BASE_URL}/auth/register", json=payload)
    return response.json(), response.status_code

def auth_login(username: str, password: str):
    data = {"username": username, "password": password}
    response = httpx.post(f"{API_BASE_URL}/auth/login", data=data)
    return response.json(), response.status_code

def get_current_user(token: str):
    response = httpx.get(f"{API_BASE_URL}/users/me", headers=_get_headers(token))
    return response.json(), response.status_code

# Categories Functions

def get_categories(token: str):
    response = httpx.get(f"{API_BASE_URL}/categories", headers=_get_headers(token))
    return response.json(), response.status_code

def create_category(token: str, name: str):
    response = httpx.post(f"{API_BASE_URL}/categories", json={"name": name}, headers=_get_headers(token))
    return response.json(), response.status_code

def delete_category(token: str, category_id: str):
    response = httpx.delete(f"{API_BASE_URL}/categories/{category_id}", headers=_get_headers(token))
    return response.json(), response.status_code

# Expenses Functions

def get_expenses(token: str, params: dict | None = None):
    response = httpx.get(f"{API_BASE_URL}/expenses", params=params, headers=_get_headers(token))
    return response.json(), response.status_code

def create_expense(token: str, expense_data: dict):
    response = httpx.post(f"{API_BASE_URL}/expenses", json=expense_data, headers=_get_headers(token))
    return response.json(), response.status_code

def delete_expense(token: str, expense_id: str):
    response = httpx.delete(f"{API_BASE_URL}/expenses/{expense_id}", headers=_get_headers(token))
    return response.json(), response.status_code

def get_summary(token: str, include_ai: bool = False):
    response = httpx.get(
        f"{API_BASE_URL}/expenses/summary",
        params={"include_ai": include_ai},
        headers=_get_headers(token),
        timeout=60.0
    )
    return response.json(), response.status_code