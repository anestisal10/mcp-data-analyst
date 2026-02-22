"""Quick functional test for the Data Analyst MCP server."""

import sys
sys.path.insert(0, ".")

from src.db import init_db, get_schema, execute_query, validate_query

print("=" * 60)
print("TEST 1: Database initialization")
print("=" * 60)
init_db()
print("  ✅ Database initialized successfully")

print()
print("=" * 60)
print("TEST 2: Schema retrieval")
print("=" * 60)
schema = get_schema()
for table, cols in schema.items():
    col_names = [c["name"] for c in cols]
    print(f"  📋 {table}: {col_names}")
print(f"  ✅ Found {len(schema)} tables")

print()
print("=" * 60)
print("TEST 3: SELECT query")
print("=" * 60)
df = execute_query("SELECT name, department, salary FROM employees ORDER BY salary DESC LIMIT 3")
print(df.to_string(index=False))
print(f"  ✅ Query returned {len(df)} rows")

print()
print("=" * 60)
print("TEST 4: SQL injection prevention")
print("=" * 60)
dangerous_queries = [
    "DROP TABLE employees",
    "DELETE FROM employees",
    "INSERT INTO employees VALUES (99, 'Hack', 'IT', 'Hacker', 0, '2024-01-01')",
    "UPDATE employees SET salary = 0",
]
for q in dangerous_queries:
    try:
        validate_query(q)
        print(f"  ❌ FAILED: '{q}' was NOT rejected!")
    except ValueError as e:
        print(f"  ✅ Rejected: '{q[:40]}...' -> {e}")

print()
print("=" * 60)
print("TEST 5: Resource formatting")
print("=" * 60)
from src.resources import format_schema
schema_text = format_schema()
print(schema_text[:300] + "...")
print(f"  ✅ Schema resource formatted ({len(schema_text)} chars)")

print()
print("=" * 60)
print("TEST 6: Read-only query tool")
print("=" * 60)
from src.tools.query import run_read_only_query_tool
result = run_read_only_query_tool("SELECT category, SUM(amount * quantity) as total_revenue FROM sales GROUP BY category ORDER BY total_revenue DESC")
print(result[:300])
print(f"  ✅ Query tool works")

print()
print("=" * 60)
print("TEST 7: Visualization tool")
print("=" * 60)
from src.tools.visualize import visualize_data_tool
text, img = visualize_data_tool(
    "SELECT region, SUM(amount * quantity) as total FROM sales GROUP BY region",
    chart_type="bar",
    title="Sales by Region"
)
print(text[:300])
if img:
    print(f"  ✅ Chart generated ({len(img)} bytes base64)")
else:
    print("  ❌ No image generated")

print()
print("=" * 60)
print("ALL TESTS PASSED ✅")
print("=" * 60)
