"""Console output: table, SQL, and error writing."""

import sys
from typing import TextIO


class ConsoleOutput:
    """Writes results and errors to stdout/stderr (or provided streams)."""

    def __init__(
        self,
        stdout: TextIO | None = None,
        stderr: TextIO | None = None,
    ) -> None:
        self._out = stdout or sys.stdout
        self._err = stderr or sys.stderr

    def print_table(self, columns: list[str], rows: list[list[str]]) -> None:
        """Print a result set as a table: header, separator, rows, row count."""
        row_count = len(rows)
        if not columns:
            print(f"({row_count} row(s))", file=self._out)
            return
        print(" | ".join(columns), file=self._out)
        sep_len = sum(len(c) for c in columns) + 3 * (len(columns) - 1)
        print("-" * sep_len, file=self._out)
        for row in rows:
            print(" | ".join(row), file=self._out)
        print(f"\n({row_count} row(s))", file=self._out)

    def print_sql(self, sql: str) -> None:
        """Print the generated SQL (e.g. for --verbose)."""
        print("SQL:", file=self._out)
        print(sql, file=self._out)
        print(file=self._out)

    def print_error(self, msg: str) -> None:
        """Print an error message to stderr."""
        print(msg, file=self._err)
