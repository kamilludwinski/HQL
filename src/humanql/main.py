"""CLI entry point and orchestration."""

import argparse
import sys

from humanql.dialect import detect, get_query_runner, get_schema_loader
from humanql.generator import ErrUnsafeSQL, SQLGenerator
from humanql.interfaces import OutputWriter, QueryRunner, SchemaLoader, TextGenerator
from humanql.llm import OpenAIClient, config_from_env
from humanql.output import ConsoleOutput
from humanql.spinner import run_spinner


def run(
    db_path: str,
    query: str,
    verbose: bool,
    dialect: str,
    schema_loader: SchemaLoader,
    llm: TextGenerator,
    runner: QueryRunner,
    output: OutputWriter,
) -> None:
    """Load schema, generate SQL, optionally print it, run query, print table. On ErrUnsafeSQL: print_error and re-raise."""
    spinner = run_spinner(stderr=sys.stderr)
    try:
        schema = schema_loader.load_schema(db_path)
        generator = SQLGenerator(llm, dialect=dialect)
        try:
            sql = generator.generate_sql(schema, query)
        except ErrUnsafeSQL:
            output.print_error("error: generated SQL was rejected (read-only allowed)")
            raise
    finally:
        spinner.stop()
    if verbose:
        output.print_sql(sql)
    columns, rows = runner.run_query(db_path, sql)
    output.print_table(columns, rows)


def main() -> None:
    """Parse CLI args, load .env, build adapters, call run(). Exit 1 on error."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        prog="humanql",
        description="Convert natural language to SQL and run it against a database (SQLite or MySQL).",
        epilog="Example: humanql --db store.db top 10 customers | humanql --db mysql://user:pass@host/db list tables",
    )
    parser.add_argument(
        "--db",
        required=True,
        help="Database: SQLite file path or mysql://user:pass@host:port/dbname (required)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print generated SQL and progress",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Natural language query",
    )
    args = parser.parse_args()
    db_path = args.db
    verbose = args.verbose
    query = " ".join(args.query or []).strip()
    if not query:
        parser.error("no natural language query provided")

    config = config_from_env()
    if not config["api_key"]:
        print("error: API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    dialect = detect(db_path)
    schema_loader = get_schema_loader(dialect)
    llm = OpenAIClient(
        base_url=config["base_url"],
        api_key=config["api_key"],
        model=config["model"],
    )
    runner = get_query_runner(dialect)
    output = ConsoleOutput(stdout=sys.stdout, stderr=sys.stderr)

    try:
        run(
            db_path=db_path,
            query=query,
            verbose=verbose,
            dialect=dialect,
            schema_loader=schema_loader,
            llm=llm,
            runner=runner,
            output=output,
        )
    except ErrUnsafeSQL:
        sys.exit(1)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
