"""
MCP Resources — expose database schema as context for the LLM.
"""

from src.db import get_schema, get_data_source_info


def format_schema() -> str:
    """
    Format the database schema as a readable string for the LLM.
    
    Returns:
        Markdown-formatted schema description.
    """
    schema = get_schema()
    source_info = get_data_source_info()

    lines = [
        f"# Database Schema",
        f"",
        f"{source_info}",
        f"",
        f"## Tables ({len(schema)})",
        f"",
    ]

    for table_name, columns in schema.items():
        lines.append(f"### `{table_name}`")
        lines.append("")
        lines.append("| Column | Type |")
        lines.append("|--------|------|")
        for col in columns:
            lines.append(f"| `{col['name']}` | {col['type']} |")
        lines.append("")

    return "\n".join(lines)
