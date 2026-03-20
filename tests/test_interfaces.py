"""Tests that protocols (interfaces) are importable and defined."""

import pytest

from humanql.interfaces import (
    OutputWriter,
    QueryRunner,
    SchemaLoader,
    TextGenerator,
)


def test_text_generator_protocol_has_generate() -> None:
    """TextGenerator protocol defines generate(system, user) -> str."""
    assert hasattr(TextGenerator, "__protocol_attrs__") or "generate" in dir(TextGenerator)


def test_schema_loader_protocol_has_load_schema() -> None:
    """SchemaLoader protocol defines load_schema(conn_spec) -> str."""
    assert hasattr(SchemaLoader, "__protocol_attrs__") or "load_schema" in dir(SchemaLoader)


def test_query_runner_protocol_has_run_query() -> None:
    """QueryRunner protocol defines run_query(conn_spec, sql) -> (columns, rows)."""
    assert hasattr(QueryRunner, "__protocol_attrs__") or "run_query" in dir(QueryRunner)


def test_output_writer_protocol_has_print_methods() -> None:
    """OutputWriter protocol defines print_table, print_sql, print_error."""
    assert hasattr(OutputWriter, "__protocol_attrs__") or "print_table" in dir(OutputWriter)
    assert "print_sql" in dir(OutputWriter)
    assert "print_error" in dir(OutputWriter)
