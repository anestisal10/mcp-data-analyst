"""Tests for src.tools — query and visualize tools."""

import pytest

from src.tools.query import run_read_only_query_tool
from src.tools.visualize import visualize_data_tool


class TestRunReadOnlyQueryTool:
    def test_returns_markdown_table(self, in_memory_db):
        result = run_read_only_query_tool("SELECT * FROM employees ORDER BY id")
        assert "Alice" in result
        assert "Bob" in result
        assert "**Results**" in result

    def test_returns_error_for_bad_sql(self, in_memory_db):
        result = run_read_only_query_tool("DROP TABLE employees")
        assert "❌" in result
        assert "Rejected" in result

    def test_returns_error_for_syntax_error(self, in_memory_db):
        result = run_read_only_query_tool("SELEC * FORM employees")
        assert "❌" in result

    def test_empty_result(self, in_memory_db):
        result = run_read_only_query_tool(
            "SELECT * FROM employees WHERE salary > 999999"
        )
        assert "no results" in result.lower()

    def test_row_count_in_header(self, in_memory_db):
        result = run_read_only_query_tool("SELECT * FROM employees")
        assert "(3 rows)" in result


class TestVisualizeDataTool:
    def test_bar_chart(self, in_memory_db):
        text, img = visualize_data_tool(
            "SELECT department, COUNT(*) as cnt FROM employees GROUP BY department",
            chart_type="bar",
            title="Departments",
        )
        assert "📊" in text
        assert "bar" in text
        assert img is not None
        assert len(img) > 100  # Non-trivial base64 string

    def test_unsupported_chart_type(self, in_memory_db):
        text, img = visualize_data_tool(
            "SELECT * FROM employees",
            chart_type="radar",
        )
        assert "❌" in text
        assert "Unsupported" in text
        assert img is None

    def test_empty_query_result(self, in_memory_db):
        text, img = visualize_data_tool(
            "SELECT * FROM employees WHERE salary > 999999",
            chart_type="bar",
        )
        assert "no results" in text.lower()
        assert img is None

    def test_invalid_sql(self, in_memory_db):
        text, img = visualize_data_tool(
            "DELETE FROM employees",
            chart_type="bar",
        )
        assert "❌" in text
        assert img is None

    def test_summary_statistics(self, in_memory_db):
        text, img = visualize_data_tool(
            "SELECT name, salary FROM employees",
            chart_type="bar",
            title="Salaries",
        )
        assert "Summary Statistics" in text
        assert img is not None

    @pytest.mark.parametrize("chart_type", ["line", "scatter", "pie", "hist"])
    def test_all_chart_types(self, in_memory_db, chart_type):
        text, img = visualize_data_tool(
            "SELECT department, COUNT(*) as cnt FROM employees GROUP BY department",
            chart_type=chart_type,
        )
        assert img is not None
