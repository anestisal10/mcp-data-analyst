"""Shared fixtures for MCP Data Analyst tests."""

import sqlite3
import pytest

import src.db as db_module


@pytest.fixture(autouse=True)
def _reset_db():
    """Reset the module-level DB connection before/after each test."""
    db_module._connection = None
    db_module._data_source_path = None
    yield
    if db_module._connection is not None:
        db_module._connection.close()
    db_module._connection = None
    db_module._data_source_path = None


@pytest.fixture()
def in_memory_db():
    """Create a minimal in-memory SQLite DB and inject it into the db module."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
        """
    )

    employees = [
        (1, "Alice", "Engineering", 70000),
        (2, "Bob", "Marketing", 55000),
        (3, "Carol", "Engineering", 65000),
    ]
    conn.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", employees)

    sales = [
        (1, "Widget", 10.0, 5),
        (2, "Gadget", 25.0, 3),
        (3, "Widget", 10.0, 8),
    ]
    conn.executemany("INSERT INTO sales VALUES (?, ?, ?, ?)", sales)
    conn.commit()

    # Inject into the db module
    db_module._connection = conn
    db_module._data_source_path = ":memory:"

    return conn
