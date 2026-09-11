# Expense Tracker Backend

A secure, asynchronous REST API for managing personal expenses, categories, and automated financial insights powered by local LLM inference.

---

## Overview

The Expense Tracker API allows users to track expenses, organize spending by custom categories, perform complex queries (filtering, sorting, pagination), and generate statistical summaries. It features an integrated local AI layer (via Ollama) that analyzes spending distributions and returns personalized financial recommendations.

---

## Tech Stack

- **Framework**: FastAPI (Python 3.12+)
- **Database & ORM**: PostgreSQL, SQLAlchemy 2.0 (AsyncIO), aiosqlite (test runtime)
- **Migrations**: Alembic (Async)
- **Authentication**: OAuth2 Password Bearer with JWT (python-jose), Argon2 password hashing (pwdlib)
- **Validation & Serialization**: Pydantic V2, Pydantic-Settings
- **AI / LLM Integration**: Ollama (local llama3.2 inference with JSON mode)
- **Testing**: Pytest, Pytest-Asyncio, HTTPX

---

## Implemented Features

### 1. Authentication & User Management

- User registration with password complexity validation and secure Argon2 hashing.
- OAuth2 password grant login producing signed JWT access tokens.
- Protected `/api/v1/users/me` endpoint verifying token claims and fetching user profile.
- Strict multi-tenancy isolation: all data queries are scoped to the authenticated user ID.

### 2. Category Management

- Full CRUD for user-scoped expense categories.
- Unique constraints preventing duplicate category names per user account.
- Cascade rules ensuring related expenses are handled on category deletion.

### 3. Expense Management & Advanced Querying

- Full CRUD for personal expenses (creation, retrieval, partial update with PATCH, deletion).
- Foreign key validation ensuring assigned categories exist and belong to the user.
- Dynamic filtering engine:
  - Filter by category UUID
  - Filter by amount boundaries (`min_amount`, `max_amount`)
  - Filter by date intervals (`start_date`, `end_date`)
- Configurable sorting (`date`, `amount`, `title`) with direction control (`asc`, `desc`).
- Offset-limit pagination (`page`, `page_size`).

### 4. Financial Analytics & Local AI Insights

- Statistical aggregations computing total lifetime spending and current month totals.
- Group-by category spending summaries calculating monetary totals and percentage shares.
- Local Ollama AI integration prompting `llama3.2` with financial metrics to generate structured financial advice, summaries, and budgeting tips in strict JSON format.

### 5. Production Hardening & Reliability

- Standardized `APIResponse[T]` envelope formatting for all endpoints (`success`, `code`, `message`, `data`).
- Centralized exception handlers for `HTTPException`, Pydantic `RequestValidationError` (422), SQLAlchemy `IntegrityError` (409), and unhandled server errors (500).
- Versioned database migrations using asynchronous Alembic.
- Automated integration test suite running on an in-memory SQLite database using `StaticPool` and `httpx.AsyncClient`.

---

## Project Structure

```text
ExpenseTracker/
├── .gitignore
├── README.md
├── plan.md
└── backend/
    ├── alembic.ini
    ├── main.py
    ├── pytest.ini
    ├── requirements.txt
    ├── app/
    │   ├── __init__.py
    │   ├── api/
    │   │   └── v1/
    │   │       └── endpoints/
    │   │           ├── auth.py
    │   │           ├── users.py
    │   │           ├── categories.py
    │   │           └── expenses.py
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── security.py
    │   │   ├── dependencies.py
    │   │   └── exceptions.py
    │   ├── db/
    │   │   ├── base.py
    │   │   └── session.py
    │   ├── models/
    │   │   ├── user.py
    │   │   ├── category.py
    │   │   └── expense.py
    │   ├── schemas/
    │   │   ├── user.py
    │   │   ├── category.py
    │   │   ├── expense.py
    │   │   ├── token.py
    │   │   └── response.py
    │   └── services/
    │       ├── user_service.py
    │       ├── category_service.py
    │       ├── expense_service.py
    │       └── ai_service.py
    ├── migrations/
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    └── tests/
        ├── conftest.py
        ├── test_auth.py
        └── test_categories.py
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database instance
- Ollama running locally with `llama3.2` model (`ollama run llama3.2`)

### 1. Environment Setup

Create a `.env` file in the `backend/` folder:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/expensetracker
JWT_KEY=your-secure-random-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
PROJECT_NAME="Expense Tracker"
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 2. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Start the Application

```bash
uvicorn main:app --reload
```

Interactive API documentation will be available at `http://localhost:8000/docs`.

### 5. Run Automated Tests

```bash
cd backend
pytest -v
```
