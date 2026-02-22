"""
Tool: run_read_only_query

Allows the LLM to execute safe, read-only SQL queries against the database.
"""

import logging

from src.db import execute_query

logger = logging.getLogger(__name__)


def run_read_only_query_tool(sql: str) -> str:
    """
    Execute a read-only SQL query and return the results.
    
    Args:
        sql: A SQL SELECT statement.
        
    Returns:
        Query results formatted as a markdown table, or an error message.
    """
    try:
        df = execute_query(sql)
    except ValueError as e:
        logger.warning("query_rejected", extra={"error": str(e)})
        return f"❌ **Query Rejected**: {e}"
    except Exception as e:
        logger.error("query_error", extra={"error": f"{type(e).__name__}: {e}"})
        return f"❌ **Query Error**: {type(e).__name__}: {e}"

    if df.empty:
        return "ℹ️ Query returned no results."

    total_rows = len(df)

    # Cap output at 100 rows to avoid overwhelming the context
    if total_rows > 100:
        df = df.head(100)
        truncation_note = f"\n\n> ⚠️ Showing first 100 of {total_rows} total rows."
    else:
        truncation_note = ""

    # Format as markdown table
    result = df.to_markdown(index=False)
    header = f"**Results** ({total_rows} rows):\n\n"

    return header + result + truncation_note
