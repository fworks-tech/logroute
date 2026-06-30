"""Root conftest: use SQLite for tests so PostgreSQL is not required."""

import os

os.environ["DATABASE_URL"] = "sqlite:///test_db.sqlite3"
