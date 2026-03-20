"""Tests for schema formatting (format_schema) and SQLite schema loader."""

import pytest

from humanql.schema import (
    Column,
    Relationship,
    SQLiteSchemaLoader,
    Table,
    format_schema,
)


def test_format_schema_empty_tables() -> None:
    """Empty tables and no relationships returns empty string."""
    assert format_schema([], []) == ""


def test_format_schema_single_table_no_columns() -> None:
    """One table with no columns: name() - 0."""
    tables = [Table(name="t", columns=[], rows=0)]
    assert format_schema(tables, []) == "t() - 0"


def test_format_schema_single_table_one_column() -> None:
    """One table, one column: t(id) - 0."""
    tables = [Table(name="users", columns=[Column(name="id", type="INTEGER")], rows=0)]
    assert format_schema(tables, []) == "users(id) - 0"


def test_format_schema_single_table_multiple_columns() -> None:
    """One table, multiple columns: t(a, b, c) - N."""
    tables = [
        Table(
            name="orders",
            columns=[
                Column(name="id", type="INTEGER"),
                Column(name="customer_id", type="INTEGER"),
                Column(name="total", type="REAL"),
            ],
            rows=42,
        )
    ]
    assert format_schema(tables, []) == "orders(id, customer_id, total) - 42"


def test_format_schema_multiple_tables() -> None:
    """Multiple tables: one line per table, sorted by name in output depends on input order."""
    tables = [
        Table(name="b", columns=[Column(name="id", type="INTEGER")], rows=1),
        Table(name="a", columns=[Column(name="x", type="TEXT")], rows=2),
    ]
    result = format_schema(tables, [])
    assert "a(x) - 2" in result
    assert "b(id) - 1" in result
    assert result.count("\n") == 1


def test_format_schema_with_relationships() -> None:
    """With relationships: tables first, then 'relationships:' and from.col -> to.col lines."""
    tables = [Table(name="orders", columns=[Column(name="customer_id", type="INTEGER")], rows=0)]
    relationships = [
        Relationship(from_table="orders", from_col="customer_id", to_table="customers", to_col="id"),
    ]
    result = format_schema(tables, relationships)
    assert result.startswith("orders(customer_id) - 0")
    assert "\nrelationships:\n" in result
    assert "orders.customer_id -> customers.id" in result


def test_format_schema_relationships_only_no_trailing_newline() -> None:
    """Relationships section has no trailing newline after last line."""
    tables = [Table(name="t", columns=[], rows=0)]
    relationships = [Relationship(from_table="t", from_col="fk", to_table="o", to_col="id")]
    result = format_schema(tables, relationships)
    assert result.endswith("t.fk -> o.id")
    assert not result.endswith("\n")


# --- SQLiteSchemaLoader ---


def test_load_schema_returns_formatted_string_with_tables(
    temp_sqlite_db: str,
) -> None:
    """Loader returns schema string containing table names and columns."""
    loader = SQLiteSchemaLoader()
    result = loader.load_schema(temp_sqlite_db)
    assert "customers" in result
    assert "orders" in result
    assert "id" in result
    assert "name" in result
    assert "customer_id" in result
    assert " - 2" in result  # customers has 2 rows
    assert " - 3" in result  # orders has 3 rows


def test_load_schema_includes_relationships(temp_sqlite_db: str) -> None:
    """Loader includes FK relationships in output."""
    loader = SQLiteSchemaLoader()
    result = loader.load_schema(temp_sqlite_db)
    assert "relationships:" in result
    assert "orders.customer_id -> customers.id" in result


def test_load_schema_empty_db_raises(empty_sqlite_db: str) -> None:
    """Loader raises clear error when DB has no user tables."""
    loader = SQLiteSchemaLoader()
    with pytest.raises(ValueError) as exc_info:
        loader.load_schema(empty_sqlite_db)
    assert "no user tables" in str(exc_info.value).lower() or "no tables" in str(
        exc_info.value
    ).lower()
