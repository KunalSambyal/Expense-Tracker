# Full-Stack Asynchronous Expense Tracker

A secure, asynchronous full-stack expense tracking platform featuring a **FastAPI** backend, **PostgreSQL** database with async **SQLAlchemy 2.0**, automated financial insights powered by a local **Ollama LLM**, and an interactive **Streamlit** frontend dashboard.

---

## Overview

The Expense Tracker enables users to log personal expenditures, organize them across custom categories, query records with dynamic filters and sorting, and visualize financial habits through an interactive analytics dashboard. The platform integrates a local Ollama instance running `llama3.2` to generate structured, personalized budget advice and saving tips directly from database aggregations.

---

## Tech Stack

### Backend

- **Framework**: FastAPI (Python 3.12+)
- **Database & ORM**: PostgreSQL, SQLAlchemy 2.0 (AsyncIO), aiosqlite (in-memory test runtime)
- **Database Migrations**: Alembic (Async)
- **Authentication & Security**: OAuth2 Password Bearer with JWT (`python-jose`), Argon2 password hashing (`pwdlib`)
- **Validation & Serialization**: Pydantic V2, Pydantic-Settings
- **AI / LLM Integration**: Ollama (local `llama3.2` inference with structured JSON formatting)
- **Testing**: Pytest, Pytest-Asyncio, HTTPX

### Frontend

- **Framework**: Streamlit
- **API Client**: HTTPX (synchronous REST integration)
- **Theming & Styling**: Native Streamlit configuration (`.streamlit/config.toml`) with custom CSS injection and modern SaaS blue accents (`#2563EB`)

---

## Implemented Features

### 1. Authentication & Multi-Tenancy

- User registration with password complexity enforcement and Argon2 hashing.
- OAuth2 password grant login producing signed JWT access tokens with user ID claims.
- Protected `/api/v1/users/me` endpoint verifying token authenticity and returning profile data.
- Strict multi-tenant data isolation: all expense and category queries are scoped to the authenticated user ID.

### 2. Category Management

- Full CRUD for user-scoped expense categories.
- Database uniqueness constraints preventing duplicate category names per user.
- Cascade deletion handling associated expenses safely.

### 3. Expense Management & Dynamic Queries

- Full CRUD for expenses (creation, listing, partial updates via `PATCH`, deletion).
- Foreign key verification ensuring assigned categories exist and belong to the user.
- Dynamic filtering engine:
    - Category UUID filter
    - Minimum and maximum amount thresholds
    - Date interval bounds (`start_date`, `end_date`)
- Configurable sorting (`date`, `amount`, `title`) and direction control (`asc`, `desc`).
- Offset-limit pagination.

### 4. Financial Analytics & Local AI Advisor

- SQL aggregations calculating total lifetime spending and current month totals.
- Group-by category spending summaries calculating monetary totals and percentage distribution.
- On-demand AI financial advisor: prompts local Ollama (`llama3.2`) with aggregated metrics to produce executive summaries and actionable savings tips in strict JSON.

### 5. Interactive Streamlit Client

- **Session State Management**: Persistent token and user session handling with clean logout mechanics.
- **Login & Register Views**: Tabbed authentication forms with real-time API error and success feedback.
- **Analytics Dashboard**: Metric cards (Total Spending, Current Month Spending, Active Categories), category breakdown bar charts, and an interactive AI financial advisor with loader spinners.
- **Expense Operations**:
    - Add expense form with dynamic category dropdowns and date pickers.
    - Live query filters (category select, minimum amount threshold, date sorting).
    - Tabular expense listing.
    - Update expander with dropdown selector that dynamically pre-fills form fields (title, amount, category index, date, description) and issues `PATCH` requests.
    - Delete expense expander with confirmation buttons.
    - Toast notifications (`st.toast`) persisting success messages across reruns.
- **Category Operations**: Side-by-side category creation form and active categories list with deletion controls.
- **Custom UI Theming**: Modern SaaS blue palette (`#2563EB`), dark mode contrast, increased base font readability, and styled toast popups.

### 6. Production Hardening & Reliability

- Standardized `APIResponse[T]` envelope for all HTTP responses (`success`, `code`, `message`, `data`).
- Centralized exception handlers for `HTTPException`, Pydantic `RequestValidationError` (422), SQLAlchemy `IntegrityError` (409), and unhandled server errors (500).
- 21 automated integration tests in `backend/tests/` running against an in-memory SQLite database using `StaticPool` and `httpx.AsyncClient`.

---

## Project Structure

```text
ExpenseTracker/
├── .gitignore
├── README.md
├── learning_plan.md
├── docs/
│   ├── advance_plan.md
│   └── plan.md
├── backend/
│   ├── alembic.ini
│   ├── main.py
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── users.py
│   │   │           ├── categories.py
│   │   │           └── expenses.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── dependencies.py
│   │   │   └── exceptions.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── category.py
│   │   │   └── expense.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── category.py
│   │   │   ├── expense.py
│   │   │   ├── token.py
│   │   │   └── response.py
│   │   └── services/
│   │       ├── user_service.py
│   │       ├── category_service.py
│   │       ├── expense_service.py
│   │       └── ai_service.py
│   ├── migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_categories.py
│       └── test_expenses.py
└── frontend/
    ├── .streamlit/
    │   └── config.toml
    ├── api_client.py
    ├── config.py
    ├── main.py
    ├── plan.md
    ├── requirements.txt
    └── streamlit_guide.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database instance
- Local Ollama instance running the `llama3.2` model (`ollama run llama3.2`)

---

### Backend Setup

1. **Environment Configuration**:
   Create a `.env` file in the `backend/` directory:

    ```env
    DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/expensetracker
    JWT_KEY=your-secure-random-secret-key
    JWT_ALGORITHM=HS256
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
    PROJECT_NAME="Expense Tracker"
    OLLAMA_HOST=http://localhost:11434
    OLLAMA_MODEL=llama3.2
    ```

2. **Install Backend Dependencies**:

    ```bash
    cd backend
    python -m venv .venv
    source .venv/bin/activate       # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Run Database Migrations**:

    ```bash
    alembic upgrade head
    ```

4. **Start the FastAPI Server**:

    ```bash
    uvicorn main:app --reload
    ```

    Interactive Swagger documentation will be accessible at `http://localhost:8000/docs`.

5. **Run Integration Tests**:
    ```bash
    pytest -v
    ```

---

### Frontend Setup

1. **Install Frontend Dependencies**:
   Open a separate terminal:

    ```bash
    cd frontend
    python -m venv .venv
    source .venv/bin/activate       # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

2. **Verify Configuration**:
   Ensure `frontend/config.py` points to your running FastAPI instance:

    ```python
    API_BASE_URL = "http://localhost:8000/api/v1"
    ```

3. **Start the Streamlit Application**:
    ```bash
    streamlit run main.py
    ```
    The application will open automatically in your browser at `http://localhost:8501`.
