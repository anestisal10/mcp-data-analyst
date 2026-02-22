"""
Database engine module — unified data access layer.

Supports:
  - SQLite databases (.db, .sqlite)
  - CSV files (.csv)
  - Excel files (.xlsx, .xls)

CSV/Excel files are loaded into an in-memory SQLite database via pandas,
making everything uniformly queryable with SQL.
"""

import logging
import os
import re
import sqlite3
import time

import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# Module-level connection
_connection: sqlite3.Connection | None = None
_data_source_path: str | None = None


def init_db(data_source: str | None = None) -> None:
    """
    Initialize the database connection.
    
    Args:
        data_source: Path to a .db/.sqlite, .csv, or .xlsx file.
                     Falls back to DATA_SOURCE env var, then to bundled sample.db.
    """
    global _connection, _data_source_path

    if _connection is not None:
        return  # Already initialized

    # Resolve data source path
    source = data_source or os.getenv("DATA_SOURCE")
    if source is None:
        # Default to bundled sample database
        source = str(Path(__file__).parent.parent / "data" / "sample.db")

    _data_source_path = source
    ext = Path(source).suffix.lower()

    if ext in (".db", ".sqlite", ".sqlite3"):
        _connection = sqlite3.connect(source)
    elif ext == ".csv":
        _connection = _load_file_to_sqlite(source, "csv")
    elif ext in (".xlsx", ".xls"):
        _connection = _load_file_to_sqlite(source, "excel")
    else:
        raise ValueError(
            f"Unsupported file type: '{ext}'. "
            "Supported: .db, .sqlite, .csv, .xlsx, .xls"
        )

    logger.info("db_initialized", extra={"source": source, "type": ext})


def _load_file_to_sqlite(path: str, file_type: str) -> sqlite3.Connection:
    """Load a CSV or Excel file into an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    table_name = Path(path).stem  # Use filename (without extension) as table name

    if file_type == "csv":
        df = pd.read_csv(path)
        df.to_sql(table_name, conn, index=False, if_exists="replace")
    elif file_type == "excel":
        # Load all sheets — each sheet becomes a separate table
        excel_file = pd.ExcelFile(path)
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            safe_name = re.sub(r"\W+", "_", sheet_name).strip("_")
            df.to_sql(safe_name, conn, index=False, if_exists="replace")

    return conn


def _ensure_connected() -> sqlite3.Connection:
    """Return the active connection, initializing if needed."""
    if _connection is None:
        init_db()
    assert _connection is not None
    return _connection


def get_schema() -> dict[str, list[dict[str, str]]]:
    """
    Get the database schema.
    
    Returns:
        Dictionary mapping table names to lists of column info dicts:
        {"table_name": [{"name": "col", "type": "TEXT"}, ...]}
    """
    conn = _ensure_connected()
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    schema: dict[str, list[dict[str, str]]] = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info('{table}')")
        columns = [
            {"name": row[1], "type": row[2] or "TEXT"}
            for row in cursor.fetchall()
        ]
        schema[table] = columns

    return schema


def validate_query(sql: str) -> None:
    """
    Validate that a SQL query is read-only using AST-level parsing.

    Uses sqlparse to parse the SQL into a token tree and walks every
    token to reject DML/DDL keywords — even when hidden inside
    subqueries, CTEs, comments, or multi-statement strings.

    Raises:
        ValueError: If the query is not a safe read-only statement.
    """
    import sqlparse
    from sqlparse.sql import Statement
    from sqlparse.tokens import Keyword, DML, DDL

    stripped = sql.strip()
    if not stripped:
        raise ValueError("Empty query.")

    statements = sqlparse.parse(stripped)

    # Block multi-statement payloads (e.g., "SELECT 1; DROP TABLE x")
    real_stmts = [s for s in statements if s.ttype is not sqlparse.tokens.Newline
                  and str(s).strip()]
    if len(real_stmts) > 1:
        raise ValueError(
            "Multiple statements detected. Only a single query is allowed."
        )

    stmt: Statement = real_stmts[0]
    stmt_type = stmt.get_type()

    # Allow: SELECT, UNKNOWN (CTEs / complex queries sqlparse can't classify)
    # Block: INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, etc.
    allowed_types = {"SELECT", "UNKNOWN"}
    if stmt_type not in allowed_types:
        raise ValueError(
            f"Only SELECT queries are allowed. Got: '{stmt_type}'. "
            "Modifications (INSERT, UPDATE, DELETE, DROP, etc.) are blocked."
        )

    # Walk the full token tree and reject any DML/DDL tokens.
    # This catches dangerous keywords hidden inside CTEs, subqueries,
    # or queries that sqlparse classified as UNKNOWN.
    _DANGEROUS_KEYWORDS = frozenset({
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
        "CREATE", "REPLACE", "ATTACH", "DETACH", "VACUUM",
    })

    def _walk_tokens(token_list):
        """Recursively yield every leaf token in the tree."""
        for token in token_list.tokens:
            if token.is_group:
                yield from _walk_tokens(token)
            else:
                yield token

    for token in _walk_tokens(stmt):
        # Check DML/DDL token types directly
        if token.ttype is DML or token.ttype is DDL:
            word = token.normalized.upper()
            if word in _DANGEROUS_KEYWORDS:
                raise ValueError(
                    f"Query contains forbidden keyword: '{word}'. "
                    "Only read-only queries are allowed."
                )

        # Also check Keyword tokens (e.g., ATTACH, VACUUM)
        if token.ttype is Keyword:
            word = token.normalized.upper()
            if word in _DANGEROUS_KEYWORDS:
                raise ValueError(
                    f"Query contains forbidden keyword: '{word}'. "
                    "Only read-only queries are allowed."
                )


def execute_query(sql: str) -> pd.DataFrame:
    """
    Execute a read-only SQL query and return results as a DataFrame.

    Args:
        sql: A SQL SELECT statement.
        
    Returns:
        pandas DataFrame with the query results.
        
    Raises:
        ValueError: If the query is not read-only.
    """
    validate_query(sql)
    conn = _ensure_connected()
    t0 = time.perf_counter()
    df = pd.read_sql_query(sql, conn)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.info(
        "query_executed",
        extra={"rows": len(df), "elapsed_ms": round(elapsed_ms, 2)},
    )
    return df


def get_data_source_info() -> str:
    """Return a human-readable description of the current data source."""
    if _data_source_path:
        return f"Connected to: {_data_source_path}"
    return "No data source connected."
