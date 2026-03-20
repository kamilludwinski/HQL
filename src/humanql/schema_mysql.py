"""MySQL schema loader: introspect via information_schema, format for LLM."""

from urllib.parse import unquote, urlparse

import pymysql

from humanql.schema import (
    Column,
    Relationship,
    Table,
    format_schema,
)


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
        "cursorclass": pymysql.cursors.DictCursor,
    }


def _quote_ident(name: str) -> str:
    """Quote identifier for MySQL (backticks)."""
    return "`" + name.replace("`", "``") + "`"


def _row_lower(row: dict) -> dict:
    """Return dict with keys lowercased (MySQL may return INFORMATION_SCHEMA columns in uppercase)."""
    return {k.lower(): v for k, v in row.items()}


class MySQLSchemaLoader:
    """Loads schema from a MySQL database as formatted text for the LLM prompt."""

    def load_schema(self, conn_spec: str) -> str:
        """Connect to MySQL, introspect tables/columns/row counts/FKs, return formatted schema."""
        kwargs = _parse_mysql_url(conn_spec)
        conn = pymysql.connect(**kwargs)
        try:
            table_names = _fetch_table_names(conn)
            if not table_names:
                raise ValueError(
                    "no user tables found — create tables or use a different database"
                )
            tables: list[Table] = []
            relationships: list[Relationship] = []
            for name in table_names:
                tables.append(_fetch_table(conn, name))
                relationships.extend(_fetch_foreign_keys(conn, name))
            tables.sort(key=lambda t: t.name)
            return format_schema(tables, relationships)
        finally:
            conn.close()


def _fetch_table_names(conn: pymysql.Connection) -> list[str]:
    """Return base table names in the current database."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        )
        return [_row_lower(row)["table_name"] for row in cur.fetchall()]


def _fetch_table(conn: pymysql.Connection, table_name: str) -> Table:
    """Return Table with columns and row count."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, data_type FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table_name,),
        )
        columns = [
            Column(name=_row_lower(row)["column_name"], type=(_row_lower(row).get("data_type") or ""))
            for row in cur.fetchall()
        ]
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS n FROM {_quote_ident(table_name)}")
        row = cur.fetchone()
        r = _row_lower(row) if row else {}
        rows = r.get("n", 0)
    return Table(name=table_name, columns=columns, rows=rows)


def _fetch_foreign_keys(conn: pymysql.Connection, table_name: str) -> list[Relationship]:
    """Return FK relationships for the table from information_schema.key_column_usage."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, referenced_table_name, referenced_column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = DATABASE() AND table_name = %s
              AND referenced_table_name IS NOT NULL
            ORDER BY ordinal_position
            """,
            (table_name,),
        )
        rels = []
        for row in cur.fetchall():
            r = _row_lower(row)
            rels.append(
                Relationship(
                    from_table=table_name,
                    from_col=r["column_name"],
                    to_table=r["referenced_table_name"],
                    to_col=r["referenced_column_name"],
                )
            )
        return rels
