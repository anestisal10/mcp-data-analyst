"""
Data Analyst MCP Server

An MCP server that connects to databases or data files and provides:
  - Schema context (as a resource)
  - Safe, read-only SQL queries (as a tool)
  - Data visualization with charts (as a tool)
"""

import logging

from mcp.server.fastmcp import FastMCP

from src.db import init_db
from src.logging_config import setup_logging
from src.resources import format_schema
from src.tools.query import run_read_only_query_tool
from src.tools.visualize import visualize_data_tool

logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("data-analyst-mcp")


# ── Resource: Database Schema ────────────────────────────────────────────────

@mcp.resource("data://schema")
def get_schema_resource() -> str:
    """
    Database schema — lists all tables with their columns and types.
    Use this to understand what data is available before writing queries.
    """
    return format_schema()


# ── Tool: Get Schema ────────────────────────────────────────────────────────

@mcp.tool()
def get_schema() -> str:
    """
    Get the database schema — lists all tables with their columns and types.

    Call this before writing queries to understand what data is available,
    which tables exist, and what columns each table has.
    """
    return format_schema()


# ── Tool: Run Read-Only Query ────────────────────────────────────────────────

@mcp.tool()
def run_read_only_query(sql: str) -> str:
    """
    Execute a safe, read-only SQL query against the database.

    Only SELECT statements are allowed. INSERT, UPDATE, DELETE, DROP, etc.
    are blocked for safety. Results are returned as a markdown table
    (capped at 100 rows).

    Args:
        sql: A SQL SELECT statement (e.g., "SELECT * FROM employees LIMIT 10")
    """
    logger.info("tool_invoked", extra={"tool": "run_read_only_query", "sql": sql[:200]})
    return run_read_only_query_tool(sql)


# ── Tool: Visualize Data ────────────────────────────────────────────────────

@mcp.tool()
def visualize_data(
    sql: str,
    chart_type: str = "bar",
    x_column: str | None = None,
    y_column: str | None = None,
    title: str = "Chart",
) -> str:
    """
    Run a SQL query and generate a chart visualization with summary statistics.

    Supported chart types: bar, line, scatter, pie, hist.
    Columns for X/Y axes are auto-detected if not specified.

    Args:
        sql: A SQL SELECT query to get the data to visualize.
        chart_type: Type of chart (bar, line, scatter, pie, hist). Default: bar.
        x_column: Column name for the X axis. Auto-detected if not specified.
        y_column: Column name for the Y axis. Auto-detected if not specified.
        title: Title for the chart. Default: "Chart".
    """
    logger.info(
        "tool_invoked",
        extra={"tool": "visualize_data", "chart_type": chart_type, "sql": sql[:200]},
    )
    text_summary, img_base64 = visualize_data_tool(
        sql, chart_type, x_column, y_column, title
    )

    if img_base64 is None:
        return text_summary

    # Return both the image and the text summary
    # The image is embedded as a data URI that MCP clients can render
    image_md = f"![{title}](data:image/png;base64,{img_base64})"
    return f"{text_summary}\n\n{image_md}"


# ── Entry Point ──────────────────────────────────────────────────────────────

def main():
    """Main entry point for the MCP server."""
    setup_logging()
    init_db()
    logger.info("server_started")
    mcp.run()


if __name__ == "__main__":
    main()
