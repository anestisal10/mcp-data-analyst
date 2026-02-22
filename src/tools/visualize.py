"""
Tool: visualize_data

Generates charts and summary statistics from SQL query results.
Uses matplotlib for rendering and returns base64-encoded PNG images.
"""

import io
import base64
import logging

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from src.db import execute_query

logger = logging.getLogger(__name__)

SUPPORTED_CHART_TYPES = ["bar", "line", "scatter", "pie", "hist"]


def visualize_data_tool(
    sql: str,
    chart_type: str = "bar",
    x_column: str | None = None,
    y_column: str | None = None,
    title: str = "Chart",
) -> tuple[str, str | None]:
    """
    Execute a SQL query and generate a visualization.
    
    Args:
        sql: SQL SELECT query to get the data.
        chart_type: Type of chart — bar, line, scatter, pie, hist.
        x_column: Column name for the X axis (auto-detected if None).
        y_column: Column name for the Y axis (auto-detected if None).
        title: Title for the chart.
    
    Returns:
        Tuple of (text_summary, base64_png_or_none).
    """
    # Execute the query
    try:
        df = execute_query(sql)
    except ValueError as e:
        logger.warning("viz_query_rejected", extra={"error": str(e)})
        return f"❌ **Query Rejected**: {e}", None
    except Exception as e:
        logger.error("viz_query_error", extra={"error": f"{type(e).__name__}: {e}"})
        return f"❌ **Query Error**: {type(e).__name__}: {e}", None

    if df.empty:
        return "ℹ️ Query returned no results — nothing to visualize.", None

    # Validate chart type
    chart_type = chart_type.lower().strip()
    if chart_type not in SUPPORTED_CHART_TYPES:
        return (
            f"❌ Unsupported chart type: '{chart_type}'. "
            f"Choose from: {', '.join(SUPPORTED_CHART_TYPES)}",
            None,
        )

    # Auto-detect columns if not specified
    if x_column is None:
        x_column = df.columns[0]
    if y_column is None and len(df.columns) > 1:
        # Pick the first numeric column for Y
        numeric_cols = df.select_dtypes(include="number").columns
        y_column = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[1]

    # Validate columns exist
    if x_column not in df.columns:
        return f"❌ Column '{x_column}' not found. Available: {list(df.columns)}", None
    if y_column and y_column not in df.columns:
        return f"❌ Column '{y_column}' not found. Available: {list(df.columns)}", None

    # Generate the chart
    try:
        img_base64 = _render_chart(df, chart_type, x_column, y_column, title)
    except Exception as e:
        logger.error("chart_render_error", extra={"error": f"{type(e).__name__}: {e}"})
        return f"❌ **Chart Error**: {type(e).__name__}: {e}", None

    logger.info(
        "chart_generated",
        extra={"chart_type": chart_type, "data_points": len(df), "image_bytes": len(img_base64)},
    )

    # Generate summary statistics
    summary_lines = [
        f"## 📊 Chart: {title}",
        f"",
        f"- **Chart type**: {chart_type}",
        f"- **Data points**: {len(df)} rows",
        f"- **X axis**: `{x_column}`",
    ]
    if y_column:
        summary_lines.append(f"- **Y axis**: `{y_column}`")

    # Add summary statistics for numeric columns
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        summary_lines.append("")
        summary_lines.append("### Summary Statistics")
        summary_lines.append("")
        summary_lines.append(numeric_df.describe().to_markdown())

    return "\n".join(summary_lines), img_base64


def _render_chart(
    df, chart_type: str, x_col: str, y_col: str | None, title: str
) -> str:
    """Render the chart and return a base64-encoded PNG string."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Apply a clean style
    plt.style.use("seaborn-v0_8-darkgrid")

    if chart_type == "bar":
        ax.bar(df[x_col].astype(str), df[y_col], color="#4C72B0", edgecolor="white")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        plt.xticks(rotation=45, ha="right")

    elif chart_type == "line":
        ax.plot(df[x_col], df[y_col], marker="o", linewidth=2, color="#4C72B0")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.fill_between(df[x_col], df[y_col], alpha=0.1, color="#4C72B0")

    elif chart_type == "scatter":
        ax.scatter(df[x_col], df[y_col], alpha=0.7, s=60, color="#4C72B0", edgecolors="white")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)

    elif chart_type == "pie":
        values = df[y_col] if y_col else df[df.columns[1]]
        labels = df[x_col].astype(str)
        colors = plt.cm.Set3.colors[:len(values)]
        ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
        ax.set_aspect("equal")

    elif chart_type == "hist":
        col = y_col or x_col
        ax.hist(df[col], bins="auto", color="#4C72B0", edgecolor="white", alpha=0.8)
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")

    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()

    # Encode to base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)

    return base64.standard_b64encode(buffer.read()).decode("utf-8")
