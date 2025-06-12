# URL Shortener API

A high-performance, asynchronous URL shortening service built with **FastAPI**, **SQLModel**, and **Async SQLAlchemy**.  
This project demonstrates clean architecture, async database access, and comprehensive testing using **pytest-asyncio** and **httpx**.

---

## Features

- **Shorten URLs** to compact, unique codes (6-15 characters, alphanumeric)
- **Redirect** short codes to original URLs with proper HTTP 307 status
- **Track visits** with IP logging and visit count statistics
- **Database** interactions fully asynchronous for high concurrency
- **Input validation** using Pydantic models with strict URL validation (`HttpUrl`)
- **Auto-generated OpenAPI docs** available at `/docs` and `/redoc`
- **Robust tests** covering all core API endpoints and edge cases

---

## Technology Stack

- **FastAPI** — Modern, fast (high-performance), web framework for building APIs with Python 3.7+
- **SQLModel** — ORM built on SQLAlchemy, designed for async support and easy data modeling
- **SQLAlchemy Async ORM** — Async capabilities for database sessions and queries
- **SQLite (in-memory)** — Default test database for fast isolated tests
- **pytest & pytest-asyncio** — Testing framework with async support
- **httpx** — Async HTTP client used for integration testing

---

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/navidsoleymani/url-shortener.git
   cd url-shortener


2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

* The API will be available at `http://localhost:8000`.
* Interactive API docs:

  * Swagger UI: `http://localhost:8000/docs`
  * ReDoc: `http://localhost:8000/redoc`

---

## API Endpoints

| Endpoint                | Method | Description                           |
| ----------------------- | ------ | ------------------------------------- |
| `/api/v1/shorten/`      | POST   | Shorten a valid original URL          |
| `/api/v1/{code}/`       | GET    | Redirect to the original URL          |
| `/api/v1/{code}/stats/` | GET    | Get visit statistics for a short code |

---

## Example Request

**Shorten a URL:**

```bash
curl -X POST "http://localhost:8000/api/v1/shorten/" -H "Content-Type: application/json" -d '{"original_url": "https://www.example.com"}'
```

Response:

```json
{
  "short_code": "a1b2c3"
}
```

**Redirect:**

Visiting `http://localhost:8000/api/v1/a1b2c3/` will redirect (307) to `https://www.example.com`.

---

## Testing

Run the full test suite with:

```bash
pytest
```

* Tests use an in-memory SQLite database for isolation and speed.
* Async fixtures ensure fresh DB state between tests.
* Includes tests for URL validation, shortening, redirection, duplicate handling, and statistics accuracy.

---

## Code Highlights

* **Async database operations** with `session.exec()` for optimized SQLModel usage
* Unique short codes generated with a mix of letters and digits, length randomized between 6 and 15 chars
* Proper use of SQLModel’s async session and transactions for consistency
* Clear separation of CRUD functions in `app/db/crud.py`
* Dependency overrides in tests to inject test database sessions seamlessly
* Extensive error handling and input validation with Pydantic

---

## Contributing

Contributions are welcome! Please fork the repo and open a PR with improvements or bug fixes.

---

## License

MIT License © 2025 Hydra

---

## Contact

For questions or support, please open an issue or contact \[[navidsoleymani@ymail.com](mailto:navidsoleymani@ymail.com)].


