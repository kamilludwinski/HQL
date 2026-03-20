"""MySQL query runner: execute read-only SQL and return columns and rows."""

from urllib.parse import unquote, urlparse

import pymysql


def _parse_mysql_url(conn_spec: str) -> dict:
    """Parse mysql://user:pass@host:port/db into dict for PyMySQL."""
    if not conn_spec.strip().lower().startswith("mysql://"):
        raise ValueError("MySQL conn_spec must start with mysql://")
    parsed = urlparse(conn_spec)
    if parsed.username is None:
        raise ValueError("MySQL URL must include user")
    password = unquote(parsed.password) if parsed.password else ""
    path = (parsed.path or "/").strip("/")
    database = path or None
    port = parsed.port or 3306
    return {
        "host": parsed.hostname or "localhost",
        "port": port,
        "user": unquote(parsed.username),
        "password": password,
        "database": database,
    }


class MySQLQueryRunner:
    """Runs a SQL query against MySQL and returns (columns, rows). NULLs as 'NULL'."""

    def run_query(self, conn_spec: str, sql: str) -> tuple[list[str], list[list[str]]]:
        """Execute the SQL and return (column_names, rows). Each cell is a string; NULL → 'NULL'."""
        kwargs = _parse_mysql_url(conn_spec)
        conn = pymysql.connect(**kwargs)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                columns = [d[0] for d in cur.description] if cur.description else []
                rows_raw = cur.fetchall()
            rows: list[list[str]] = []
            for row in rows_raw:
                vals = ["NULL" if v is None else str(v) for v in row]
                rows.append(vals)
            return (columns, rows)
        finally:
            conn.close()
