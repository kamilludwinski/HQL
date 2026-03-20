"""Tests for run() orchestration with mocked dependencies."""

from unittest.mock import MagicMock

import pytest

from humanql.generator import ErrUnsafeSQL
from humanql.main import run


def test_run_calls_load_schema_then_generate_then_run_query_then_print_table() -> None:
    """run() calls schema_loader.load_schema, then generator (via llm), then runner.run_query, then output.print_table."""
    schema_loader = MagicMock()
    schema_loader.load_schema.return_value = "users(id, name) - 0"
    llm = MagicMock()
    llm.generate.return_value = "SELECT id, name FROM users;"
    runner = MagicMock()
    runner.run_query.return_value = (["id", "name"], [["1", "alice"]])
    output = MagicMock()

    run(
        db_path="/path/to/db",
        query="list users",
        verbose=False,
        dialect="sqlite",
        schema_loader=schema_loader,
        llm=llm,
        runner=runner,
        output=output,
    )

    schema_loader.load_schema.assert_called_once_with("/path/to/db")
    llm.generate.assert_called_once()
    call_args = llm.generate.call_args[0]
    assert "users(id, name)" in call_args[1]
    assert "list users" in call_args[1]
    runner.run_query.assert_called_once_with("/path/to/db", "SELECT id, name FROM users;")
    output.print_table.assert_called_once_with(["id", "name"], [["1", "alice"]])


def test_run_verbose_calls_print_sql() -> None:
    """When verbose=True, run() calls output.print_sql with the generated SQL."""
    schema_loader = MagicMock(return_value="t(x) - 0")
    schema_loader.load_schema.return_value = "t(x) - 0"
    llm = MagicMock()
    llm.generate.return_value = "SELECT x FROM t;"
    runner = MagicMock()
    runner.run_query.return_value = ([], [])
    output = MagicMock()

    run(
        db_path="/db",
        query="q",
        verbose=True,
        dialect="sqlite",
        schema_loader=schema_loader,
        llm=llm,
        runner=runner,
        output=output,
    )

    output.print_sql.assert_called_once_with("SELECT x FROM t;")
    output.print_table.assert_called_once()


def test_run_unsafe_sql_calls_print_error_and_does_not_run_query() -> None:
    """When generator raises ErrUnsafeSQL, run() calls output.print_error and does not call runner.run_query."""
    schema_loader = MagicMock()
    schema_loader.load_schema.return_value = "t(x) - 0"
    llm = MagicMock()
    llm.generate.return_value = "DELETE FROM t;"
    runner = MagicMock()
    output = MagicMock()

    with pytest.raises(ErrUnsafeSQL):
        run(
            db_path="/db",
            query="q",
            verbose=False,
            dialect="sqlite",
            schema_loader=schema_loader,
            llm=llm,
            runner=runner,
            output=output,
        )

    output.print_error.assert_called_once()
    assert "read-only" in output.print_error.call_args[0][0].lower() or "rejected" in output.print_error.call_args[0][0].lower()
    runner.run_query.assert_not_called()
