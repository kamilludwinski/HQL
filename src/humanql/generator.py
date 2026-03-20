"""SQL generation: prompts, normalize, validate read-only SQL."""

import re

from humanql.interfaces import TextGenerator


class ErrUnsafeSQL(Exception):
    """Raised when generated SQL is not read-only (e.g. contains DELETE, DROP)."""

    pass


_FORBIDDEN_PATTERN = re.compile(
    r"(?i)\b(DELETE|UPDATE|DROP|INSERT|ALTER|TRUNCATE)\b"
)


def _strip_markdown_sql(s: str) -> str:
    """Remove ```sql ... ``` or ``` ... ``` fences."""
    s = s.strip()
    prefix = "```"
    if not s.startswith(prefix):
        return s
    s = s[len(prefix) :].strip()
    if s.lower().startswith("sql"):
        s = s[3:].strip()
    s = s.removesuffix("```").strip()
    return s


def normalize_sql(s: str) -> str:
    """Strip markdown, keep only the first statement up to ';', ensure trailing ';', trim."""
    s = _strip_markdown_sql(s.strip())
    i = s.find(";")
    if i != -1:
        s = s[: i + 1]
    s = s.strip()
    if s and not s.endswith(";"):
        s += ";"
    return s.strip()


def validate_read_only_sql(sql: str) -> None:
    """Raise ErrUnsafeSQL if SQL is empty, does not start with SELECT/WITH/SHOW, or contains forbidden keywords."""
    sql = sql.strip()
    if not sql:
        raise ErrUnsafeSQL("empty sql")
    upper = sql.upper()
    allowed_starts = ("SELECT", "WITH", "SHOW")
    if not any(upper.startswith(s) for s in allowed_starts):
        raise ErrUnsafeSQL("query must start with SELECT, WITH, or SHOW")
    if _FORBIDDEN_PATTERN.search(sql):
        raise ErrUnsafeSQL("read-only SQL only; forbidden keyword present")


_SQLITE_SYSTEM_PROMPT = """You are a SQL generator.
Rules:
- Output only valid SQLite SQL
- Generate exactly one query
- The query must be read-only
- Use only tables and columns that appear in the schema (no invented columns like age or created_at unless they are listed)
- If the user asks for data that has no matching column in the schema, use NULL for it; do not use constants or formulas for non-existent columns
- Do not include explanations or markdown"""

_MYSQL_SYSTEM_PROMPT = """You are a SQL generator.
Rules:
- Output only valid MySQL SQL
- Generate exactly one query
- The query must be read-only
- Use only tables and columns that appear in the schema (no invented columns like age or created_at unless they are listed)
- If the user asks for data that has no matching column in the schema, use NULL for it; do not use constants or formulas for non-existent columns
- Do not include explanations or markdown"""


def _build_user_prompt(schema: str, query: str) -> str:
    """Build user prompt: schema then query."""
    return f"Database schema:\n\n{schema}\n\n{query.strip()}"


def _system_prompt(dialect: str) -> str:
    """Return the system prompt for the given dialect (sqlite or mysql)."""
    if dialect == "mysql":
        return _MYSQL_SYSTEM_PROMPT
    return _SQLITE_SYSTEM_PROMPT


class SQLGenerator:
    """Generates read-only SQL from natural language using a TextGenerator and schema."""

    def __init__(self, text_generator: TextGenerator, dialect: str = "sqlite") -> None:
        self._gen = text_generator
        self._dialect = dialect

    def generate_sql(self, schema: str, natural_language_query: str) -> str:
        """Return a single normalized, validated SELECT/WITH statement. Raises ErrUnsafeSQL if invalid."""
        user_prompt = _build_user_prompt(schema, natural_language_query)
        raw = self._gen.generate(_system_prompt(self._dialect), user_prompt)
        sql = normalize_sql(raw)
        validate_read_only_sql(sql)
        return sql
