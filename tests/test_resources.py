"""Tests for src.resources — schema formatting."""

from src.resources import format_schema


class TestFormatSchema:
    def test_contains_header(self, in_memory_db):
        text = format_schema()
        assert "# Database Schema" in text

    def test_contains_all_tables(self, in_memory_db):
        text = format_schema()
        assert "`employees`" in text
        assert "`sales`" in text

    def test_contains_column_names(self, in_memory_db):
        text = format_schema()
        assert "`name`" in text
        assert "`salary`" in text
        assert "`amount`" in text

    def test_markdown_table_format(self, in_memory_db):
        text = format_schema()
        assert "| Column | Type |" in text
        assert "|--------|------|" in text

    def test_contains_source_info(self, in_memory_db):
        text = format_schema()
        assert "Connected to:" in text
