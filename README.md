# HQL - Human Query Language (Python)

Query a database using natural language. HQL converts your question into read-only SQL via an OpenAI-compatible API, runs it, and prints the results.

**Supports SQLite and MySQL.** Use a file path for SQLite, or `mysql://user:pass@host:port/dbname` for MySQL.

## Usage

```bash
# SQLite
humanql --db <path-to-sqlite.db> "<your question>"

# MySQL
humanql --db "mysql://user:pass@host:3306/dbname" "<your question>"
```

Examples:

```bash
./run.sh --db store.db "list all customers"
./run.sh --db store.db -v "top 10 orders by total"
./run.sh --db "mysql://humanql:humanql@127.0.0.1:3306/humanql" "list all tables"
```

- **`--db`** (required) – SQLite file path or MySQL URL (`mysql://user:password@host:port/database`).
- **`-v` / `--verbose`** – Print the generated SQL before the result table.

## Environment

Set variables in a `.env` file (see `.env.example`). They are loaded automatically if `python-dotenv` is installed.

- **API_KEY** (required) – API key for an OpenAI-compatible chat endpoint (e.g. OpenAI, Groq).
- **BASE_URL** (optional) – Default `https://api.openai.com/v1`. For Groq use `https://api.groq.com/openai/v1`.
- **MODEL** (optional) – Default `gpt-4o-mini`.

You can get a free API key from [Groq](https://console.groq.com/keys).

## Safety

Only **read-only** SQL is executed. The tool rejects any generated query that:

- Does not start with `SELECT` or `WITH`
- Contains the keywords: `DELETE`, `UPDATE`, `DROP`, `INSERT`, `ALTER`, `TRUNCATE`

## Quickstart

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. For windows make sure to install latest sql drivers
   `https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17`

3. Copy `.env.example` to `.env` and set `API_KEY`.

4. Spin up docker container (MySQL) or create .db file (SQLite) [instructions below]

5. Query

### Manual test

From the repo root:

- SQLite

```bash
./scripts/create-sqlite.db.sh
```

to create sqlite db and then

```bash
./run.sh --db sqlite.db <your question>
```

- MySql

```bash
./scripts/run-mysql-docker.sh
```

to spin up a docker container

## Tests

Install dev dependencies and run pytest:

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```
