"""Pytest configuration: add src to path so humanql package is importable."""

import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


@pytest.fixture
def temp_sqlite_db() -> str:
    """Create a temporary SQLite DB with two tables and a FK; return path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, "
        "FOREIGN KEY (customer_id) REFERENCES customers(id))"
    )
    conn.execute("INSERT INTO customers (id, name) VALUES (1, 'alice'), (2, 'bob')")
    conn.execute("INSERT INTO orders (id, customer_id) VALUES (1, 1), (2, 1), (3, 2)")
    conn.commit()
    conn.close()
    yield path
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def empty_sqlite_db() -> str:
    """Create an empty SQLite DB (no user tables); return path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    sqlite3.connect(path).close()
    yield path
    Path(path).unlink(missing_ok=True)
