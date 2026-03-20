"""Tests for SQL generator: normalize_sql, validate_read_only_sql, SQLGenerator."""

import pytest

from humanql.generator import (
    ErrUnsafeSQL,
    SQLGenerator,
    normalize_sql,
    validate_read_only_sql,
)


# --- normalize_sql ---


def test_normalize_sql_plain_statement() -> None:
    """Plain SQL is trimmed and gets semicolon if missing."""
    assert normalize_sql("SELECT 1") == "SELECT 1;"
    assert normalize_sql("  SELECT 1  ") == "SELECT 1;"


def test_normalize_sql_already_has_semicolon() -> None:
    """SQL that already ends with ; is unchanged (except trim)."""
    assert normalize_sql("SELECT 1;") == "SELECT 1;"


def test_normalize_sql_takes_first_statement_only() -> None:
    """Only the first statement up to ; is kept."""
    assert normalize_sql("SELECT 1; SELECT 2;") == "SELECT 1;"
    assert normalize_sql("SELECT a FROM t; DROP TABLE t;") == "SELECT a FROM t;"


def test_normalize_sql_strips_markdown_sql_fence() -> None:
    """```sql ... ``` is stripped."""
    raw = "```sql\nSELECT 1;\n```"
    assert normalize_sql(raw) == "SELECT 1;"


def test_normalize_sql_strips_markdown_generic_fence() -> None:
    """``` ... ``` (no 'sql' tag) is stripped."""
    raw = "```\nSELECT 1;\n```"
    assert normalize_sql(raw) == "SELECT 1;"


def test_normalize_sql_strips_markdown_with_leading_trailing_whitespace() -> None:
    """Markdown fence with surrounding whitespace is stripped."""
    raw = "  ```  \n  sql  \n  SELECT 1;  \n  ```  "
    assert normalize_sql(raw) == "SELECT 1;"


def test_normalize_sql_empty_after_strip_returns_empty() -> None:
    """Empty or whitespace-only input returns empty string."""
    assert normalize_sql("") == ""
    assert normalize_sql("   ") == ""
    assert normalize_sql("```\n```") == ""


# --- validate_read_only_sql ---


def test_validate_read_only_accepts_select() -> None:
    """SELECT ... is accepted (case insensitive)."""
    validate_read_only_sql("SELECT 1")
    validate_read_only_sql("select * from t")
    validate_read_only_sql("  SELECT id FROM users  ")


def test_validate_read_only_accepts_with() -> None:
    """WITH ... SELECT is accepted."""
    validate_read_only_sql("WITH x AS (SELECT 1) SELECT * FROM x")
    validate_read_only_sql("with cte as (select 1) select * from cte")


def test_validate_read_only_accepts_show() -> None:
    """SHOW ... is accepted (e.g. MySQL SHOW TABLES)."""
    validate_read_only_sql("SHOW TABLES")
    validate_read_only_sql("show tables")


def test_validate_read_only_rejects_empty() -> None:
    """Empty or whitespace-only SQL raises ErrUnsafeSQL."""
    with pytest.raises(ErrUnsafeSQL):
        validate_read_only_sql("")
    with pytest.raises(ErrUnsafeSQL):
        validate_read_only_sql("   ")


def test_validate_read_only_rejects_non_select_with_show() -> None:
    """SQL that does not start with SELECT, WITH, or SHOW raises ErrUnsafeSQL."""
    with pytest.raises(ErrUnsafeSQL):
        validate_read_only_sql("INSERT INTO t VALUES (1)")
    with pytest.raises(ErrUnsafeSQL):
        validate_read_only_sql("DELETE FROM t")
    with pytest.raises(ErrUnsafeSQL):
        validate_read_only_sql("UPDATE t SET x = 1")


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM delete_log",
        "SELECT delete_flag FROM t",
        "SELECT * FROM t WHERE x IN (SELECT id FROM updates)",
    ],
)
def test_validate_read_only_accepts_forbidden_word_in_identifier(sql: str) -> None:
    """Forbidden keywords as part of identifier (e.g. delete_log) are allowed (word boundary)."""
    validate_read_only_sql(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1; DELETE FROM t",
        "SELECT * FROM t; UPDATE t SET x=1",
        "WITH x AS (SELECT 1) DROP TABLE t",
        "SELECT * FROM t TRUNCATE",
    ],
)
def test_validate_read_only_rejects_forbidden_keyword_present(sql: str) -> None:
    """SQL containing DELETE, UPDATE, DROP, INSERT, ALTER, or TRUNCATE as word raises ErrUnsafeSQL."""
    with pytest.raises(ErrUnsafeSQL):
        validate_read_only_sql(sql)


@pytest.mark.parametrize(
    "keyword",
    ["DELETE", "UPDATE", "DROP", "INSERT", "ALTER", "TRUNCATE"],
)
def test_validate_read_only_rejects_each_forbidden_keyword(keyword: str) -> None:
    """Each forbidden keyword (case insensitive) causes rejection."""
    with pytest.raises(ErrUnsafeSQL):
        validate_read_only_sql(f"SELECT 1; {keyword} FROM t")
    with pytest.raises(ErrUnsafeSQL):
        validate_read_only_sql(keyword.lower() + " from t")


# --- SQLGenerator ---


def test_sql_generator_user_prompt_contains_schema_and_query() -> None:
    """generate_sql passes schema and query in the user prompt to the LLM."""
    schema = "users(id, name) - 10"
    query = "list all names"
    received_user = []

    class MockGen:
        def generate(self, system: str, user: str) -> str:
            received_user.append(user)
            return "SELECT name FROM users;"

    gen = SQLGenerator(MockGen())
    gen.generate_sql(schema, query)
    assert len(received_user) == 1
    assert "Database schema:" in received_user[0]
    assert schema in received_user[0]
    assert query in received_user[0]


def test_sql_generator_returns_normalized_valid_sql() -> None:
    """generate_sql returns normalized and validated SQL (e.g. markdown stripped)."""
    class MockGen:
        def generate(self, system: str, user: str) -> str:
            return "```sql\nSELECT 1;\n```"

    gen = SQLGenerator(MockGen())
    result = gen.generate_sql("t(x) - 0", "count")
    assert result == "SELECT 1;"


def test_sql_generator_unsafe_sql_raises() -> None:
    """When LLM returns DELETE/UPDATE etc., generate_sql raises ErrUnsafeSQL."""
    class MockGen:
        def generate(self, system: str, user: str) -> str:
            return "DELETE FROM users;"

    gen = SQLGenerator(MockGen())
    with pytest.raises(ErrUnsafeSQL):
        gen.generate_sql("users(id) - 0", "delete everyone")
