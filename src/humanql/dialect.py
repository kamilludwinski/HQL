"""Detect database dialect from connection spec and return loader/runner."""

from humanql.exec_mysql import MySQLQueryRunner
from humanql.exec_sqlite import SQLiteQueryRunner
from humanql.schema import SQLiteSchemaLoader
from humanql.schema_mysql import MySQLSchemaLoader


def detect(conn_spec: str) -> str:
    """Return 'mysql' if conn_spec starts with mysql://, else 'sqlite'."""
    s = conn_spec.strip().lower()
    if s.startswith("mysql://"):
        return "mysql"
    return "sqlite"


def get_schema_loader(dialect: str):
    """Return the SchemaLoader for the given dialect."""
    if dialect == "mysql":
        return MySQLSchemaLoader()
    return SQLiteSchemaLoader()


def get_query_runner(dialect: str):
    """Return the QueryRunner for the given dialect."""
    if dialect == "mysql":
        return MySQLQueryRunner()
    return SQLiteQueryRunner()
