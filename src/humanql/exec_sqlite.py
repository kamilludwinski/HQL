"""SQLite query runner: execute read-only SQL and return columns and rows."""

import sqlite3


class SQLiteQueryRunner:
    """Runs a SQL query against SQLite and returns (columns, rows). NULLs as 'NULL'."""

    def run_query(self, conn_spec: str, sql: str) -> tuple[list[str], list[list[str]]]:
        """Execute the SQL and return (column_names, rows). Each cell is a string; NULL → 'NULL'."""
        conn = sqlite3.connect(conn_spec)
        try:
            cur = conn.execute(sql)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows_raw = cur.fetchall()
            rows: list[list[str]] = []
            for row in rows_raw:
                vals = []
                for v in row:
                    vals.append("NULL" if v is None else str(v))
                rows.append(vals)
            return (columns, rows)
        finally:
            conn.close()
