# EdgeLog — Trading Journal

A full-stack trading journal built with Flask, Python, and SQLite.

## Features

- **Log trades** — instrument, direction, setup, session, prices, notes
- **Auto-calculated P&L and R-multiple** on closed trades
- **Flag notable trades** for quick review
- **Search and filter** by instrument, direction, status, or flagged
- **Dashboard** with equity curve chart and key stats
- **User authentication** — register, login, logout (Flask-Login)
- **Swappable data layer** — SQLite (production) or in-memory (testing) via config
- **Unit tested** with pytest

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Python 3.11+, Flask 3             |
| ORM         | SQLAlchemy + Flask-SQLAlchemy     |
| Auth        | Flask-Login, Werkzeug password hash |
| Forms       | Flask-WTF, WTForms                |
| Frontend    | Jinja2, HTML5, CSS3, Canvas API   |
| Database    | SQLite (dev/prod), in-memory (test)|
| Testing     | pytest, pytest-flask              |

## Architecture

```
app/
├── blueprints/         # auth / dashboard / trades
├── repository/         # abstract.py → sqlite_repo.py | memory_repo.py
├── services/           # TradeService, UserService
├── models.py           # SQLAlchemy models (User, Trade)
├── templates/          # Jinja2 HTML
└── static/             # CSS, JS
```

The **Repository pattern** fully decouples the service layer from the database. Swap `REPOSITORY=memory` in your `.env` to run entirely in-memory (used automatically during testing).

## Setup

```bash
# 1. Clone and enter the project
cd TradeJournal

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and configure environment
cp .env .env.local   # edit SECRET_KEY for production

# 5. Run
python run.py
```

Visit `http://localhost:5000` — register an account and start journaling.

## Running Tests

```bash
pytest tests/ -v
```

## Switching the Data Layer

In `.env`:

```
REPOSITORY=sqlite   # uses tradejournal.db
REPOSITORY=memory   # fully in-memory, no DB file
```

No application code changes required.
