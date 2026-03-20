"""Protocols (interfaces) for schema loading, LLM, query execution, and output."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class TextGenerator(Protocol):
    """Generates text from system and user prompts (e.g. OpenAI-compatible chat)."""

    def generate(self, system: str, user: str) -> str:
        """Return generated text (e.g. SQL) from the model. Raises on API error."""
        ...


@runtime_checkable
class SchemaLoader(Protocol):
    """Loads database schema as formatted text for a given connection."""

    def load_schema(self, conn_spec: str) -> str:
        """Connect to the database and return schema as a single string for the LLM prompt."""
        ...


@runtime_checkable
class QueryRunner(Protocol):
    """Runs a read-only SQL query and returns columns and rows."""

    def run_query(self, conn_spec: str, sql: str) -> tuple[list[str], list[list[str]]]:
        """Execute the SQL and return (column_names, rows). NULLs as the string 'NULL'."""
        ...


@runtime_checkable
class OutputWriter(Protocol):
    """Writes results and errors to stdout/stderr."""

    def print_table(self, columns: list[str], rows: list[list[str]]) -> None:
        """Print a result set as a table (header, separator, rows, row count)."""
        ...

    def print_sql(self, sql: str) -> None:
        """Print the generated SQL (e.g. for --verbose)."""
        ...

    def print_error(self, msg: str) -> None:
        """Print an error message to stderr."""
        ...
