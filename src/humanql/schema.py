"""Schema types and formatting for LLM prompt; SQLite schema loader."""

import sqlite3
from dataclasses import dataclass


@dataclass
class Column:
    """Column name and type."""

    name: str
    type: str


@dataclass
class Table:
    """Table name, columns, and row count."""

    name: str
    columns: list[Column]
    rows: int


@dataclass
class Relationship:
    """Foreign key: from_table.from_col -> to_table.to_col."""

    from_table: str
    from_col: str
    to_table: str
    to_col: str


def format_schema(tables: list[Table], relationships: list[Relationship]) -> str:
    """Format tables and relationships as text for the LLM prompt.

    Format: one line per table as "name(col1, col2) - N";
    if relationships, then "\\nrelationships:\\n" and "from_table.from_col -> to_table.to_col" per line.
    No trailing newline.
    """
    lines: list[str] = []
    for t in tables:
        col_names = [c.name for c in t.columns]
        lines.append(f"{t.name}({', '.join(col_names)}) - {t.rows}")
    if relationships:
        lines.append("relationships:")
        for r in relationships:
            lines.append(f"{r.from_table}.{r.from_col} -> {r.to_table}.{r.to_col}")
    return "\n".join(lines)


def _quote_ident(name: str) -> str:
    """Quote identifier for SQLite (escape double quotes)."""
    return '"' + name.replace('"', '""') + '"'


class SQLiteSchemaLoader:
    """Loads schema from a SQLite database as formatted text for the LLM prompt."""

    def load_schema(self, conn_spec: str) -> str:
        """Connect to SQLite, introspect tables/columns/row counts/FKs, return formatted schema."""
        conn = sqlite3.connect(conn_spec)
        try:
            conn.row_factory = sqlite3.Row
            table_names = _fetch_table_names(conn)
            if not table_names:
                raise ValueError(
                    f"no user tables found in {conn_spec!r} — create the DB first or use a different database"
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


def _fetch_table_names(conn: sqlite3.Connection) -> list[str]:
    """Return user table names (exclude sqlite_%)."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    return [row[0] for row in cur.fetchall()]


def _fetch_table(conn: sqlite3.Connection, table_name: str) -> Table:
    """Return Table with columns and row count."""
    cur = conn.execute(f"PRAGMA table_info({_quote_ident(table_name)})")
    columns = [Column(name=row[1], type=row[2] or "") for row in cur.fetchall()]
    cur = conn.execute(f"SELECT COUNT(*) FROM {_quote_ident(table_name)}")
    rows = cur.fetchone()[0]
    return Table(name=table_name, columns=columns, rows=rows)


def _fetch_foreign_keys(conn: sqlite3.Connection, table_name: str) -> list[Relationship]:
    """Return FK relationships for the table. PRAGMA foreign_key_list: id, seq, table, from, to."""
    cur = conn.execute(f"PRAGMA foreign_key_list({_quote_ident(table_name)})")
    rels = []
    for row in cur.fetchall():
        # row: (id, seq, table, from, to, on_update, on_delete, match)
        to_table = row[2]
        from_col = row[3]
        to_col = row[4]
        rels.append(
            Relationship(
                from_table=table_name,
                from_col=from_col,
                to_table=to_table,
                to_col=to_col,
            )
        )
    return rels
