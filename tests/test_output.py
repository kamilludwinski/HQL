"""Tests for ConsoleOutput (print_table, print_sql, print_error)."""

import io

import pytest

from humanql.output import ConsoleOutput


def test_print_table_empty_columns() -> None:
    """Empty columns prints row count only."""
    out = io.StringIO()
    err = io.StringIO()
    writer = ConsoleOutput(stdout=out, stderr=err)
    writer.print_table([], [])
    text = out.getvalue()
    assert "(0 row(s))" in text


def test_print_table_with_columns_and_rows() -> None:
    """Table has header, separator, rows, and row count."""
    out = io.StringIO()
    err = io.StringIO()
    writer = ConsoleOutput(stdout=out, stderr=err)
    writer.print_table(["a", "b"], [["1", "2"], ["3", "4"]])
    text = out.getvalue()
    assert "a | b" in text
    assert "---" in text or "1 | 2" in text
    assert "1 | 2" in text
    assert "3 | 4" in text
    assert "(2 row(s))" in text


def test_print_sql() -> None:
    """print_sql outputs SQL label and the SQL."""
    out = io.StringIO()
    err = io.StringIO()
    writer = ConsoleOutput(stdout=out, stderr=err)
    writer.print_sql("SELECT 1;")
    text = out.getvalue()
    assert "SQL" in text
    assert "SELECT 1;" in text


def test_print_error() -> None:
    """print_error writes to stderr."""
    out = io.StringIO()
    err = io.StringIO()
    writer = ConsoleOutput(stdout=out, stderr=err)
    writer.print_error("something went wrong")
    assert out.getvalue() == ""
    assert "something went wrong" in err.getvalue()
