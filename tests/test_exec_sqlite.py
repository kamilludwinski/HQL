"""Tests for SQLite query runner."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from humanql.exec_sqlite import SQLiteQueryRunner


@pytest.fixture
def temp_db() -> str:
    """Temp SQLite file path; caller creates schema and data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)


def test_run_query_returns_columns_and_rows(temp_db: str) -> None:
    """run_query returns column names and rows."""
    conn = sqlite3.connect(temp_db)
    conn.execute("CREATE TABLE t (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO t VALUES (1, 'a'), (2, 'b')")
    conn.commit()
    conn.close()
    runner = SQLiteQueryRunner()
    columns, rows = runner.run_query(temp_db, "SELECT id, name FROM t")
    assert columns == ["id", "name"]
    assert rows == [["1", "a"], ["2", "b"]]


def test_run_query_null_as_string_null(temp_db: str) -> None:
    """NULL values in result are returned as the string 'NULL'."""
    conn = sqlite3.connect(temp_db)
    conn.execute("CREATE TABLE t (a TEXT, b TEXT)")
    conn.execute("INSERT INTO t VALUES ('x', NULL), (NULL, 'y')")
    conn.commit()
    conn.close()
    runner = SQLiteQueryRunner()
    _, rows = runner.run_query(temp_db, "SELECT a, b FROM t")
    assert len(rows) == 2
    assert ["x", "NULL"] in rows
    assert ["NULL", "y"] in rows


def test_run_query_empty_result(temp_db: str) -> None:
    """Empty result returns columns and empty rows list."""
    conn = sqlite3.connect(temp_db)
    conn.execute("CREATE TABLE t (id INTEGER)")
    conn.commit()
    conn.close()
    runner = SQLiteQueryRunner()
    columns, rows = runner.run_query(temp_db, "SELECT id FROM t WHERE 1=0")
    assert columns == ["id"]
    assert rows == []
