"""Tests for src.db — schema, validation, and query execution."""

import pytest

from src.db import get_schema, validate_query, execute_query


class TestGetSchema:
    def test_returns_all_tables(self, in_memory_db):
        schema = get_schema()
        assert set(schema.keys()) == {"employees", "sales"}

    def test_column_info(self, in_memory_db):
        schema = get_schema()
        emp_cols = {c["name"] for c in schema["employees"]}
        assert emp_cols == {"id", "name", "department", "salary"}

    def test_column_types(self, in_memory_db):
        schema = get_schema()
        type_map = {c["name"]: c["type"] for c in schema["employees"]}
        assert type_map["id"] == "INTEGER"
        assert type_map["name"] == "TEXT"
        assert type_map["salary"] == "REAL"


class TestValidateQuery:
    @pytest.mark.parametrize(
        "sql",
        [
            "SELECT * FROM employees",
            "  SELECT name FROM employees  ",
            "WITH cte AS (SELECT 1) SELECT * FROM cte",
            "EXPLAIN SELECT 1",
            "PRAGMA table_info('employees')",
        ],
    )
    def test_allows_safe_queries(self, sql):
        validate_query(sql)  # Should not raise

    @pytest.mark.parametrize(
        "sql",
        [
            "DROP TABLE employees",
            "DELETE FROM employees",
            "INSERT INTO employees VALUES (99, 'Hack', 'IT', 0)",
            "UPDATE employees SET salary = 0",
            "ALTER TABLE employees ADD COLUMN x TEXT",
            "CREATE TABLE evil (id INT)",
            "ATTACH DATABASE ':memory:' AS hack",
        ],
    )
    def test_rejects_dangerous_queries(self, sql):
        with pytest.raises(ValueError):
            validate_query(sql)

    def test_rejects_empty_query(self):
        with pytest.raises(ValueError, match="Empty query"):
            validate_query("   ")

    def test_rejects_hidden_dangerous_keywords(self):
        """A SELECT that embeds a dangerous keyword should still be rejected."""
        with pytest.raises(ValueError):
            validate_query("SELECT * FROM employees; DROP TABLE employees")

    def test_rejects_multi_statement_injection(self):
        """Block semicolon-separated payloads — even if the first is safe."""
        with pytest.raises(ValueError):
            validate_query("SELECT 1; DELETE FROM employees")

    def test_rejects_comment_wrapped_attack(self):
        """Block dangerous statements even with comment obfuscation."""
        with pytest.raises(ValueError):
            validate_query("DROP /* sneaky */ TABLE employees")

    def test_rejects_subquery_injection(self):
        """Block writes hidden inside subqueries."""
        with pytest.raises(ValueError):
            validate_query(
                "SELECT * FROM (DELETE FROM employees RETURNING *)"
            )

    def test_allows_column_named_like_keyword(self):
        """Column aliases like 'update_count' shouldn't trigger false positives."""
        # sqlparse correctly identifies 'update_count' as an identifier, not DML
        validate_query("SELECT COUNT(*) AS update_count FROM employees")


class TestExecuteQuery:
    def test_returns_dataframe(self, in_memory_db):
        df = execute_query("SELECT * FROM employees")
        assert len(df) == 3
        assert list(df.columns) == ["id", "name", "department", "salary"]

    def test_aggregation(self, in_memory_db):
        df = execute_query(
            "SELECT department, COUNT(*) as cnt FROM employees GROUP BY department"
        )
        assert len(df) == 2

    def test_rejects_write_query(self, in_memory_db):
        with pytest.raises(ValueError):
            execute_query("DELETE FROM employees WHERE id = 1")
