"""
Create a sample SQLite database with demo data for the MCP server.

Run this script to generate data/sample.db:
    python create_sample_db.py
"""

import sqlite3
from pathlib import Path


def create_sample_db():
    db_path = Path(__file__).parent / "data" / "sample.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove old DB if it exists
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # ── Table: employees ─────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL NOT NULL,
            hire_date TEXT NOT NULL
        )
    """)

    employees = [
        (1,  "Αλέξανδρος Παπαδόπουλος", "Engineering",  "Senior Developer",  65000, "2020-03-15"),
        (2,  "Μαρία Κωνσταντίνου",      "Engineering",  "Junior Developer",  42000, "2022-07-01"),
        (3,  "Νίκος Δημητρίου",          "Marketing",    "Marketing Manager", 58000, "2019-11-20"),
        (4,  "Ελένη Γεωργίου",           "Marketing",    "Content Creator",   38000, "2023-01-10"),
        (5,  "Δημήτρης Αντωνίου",        "Sales",        "Sales Lead",        55000, "2021-05-18"),
        (6,  "Σοφία Παπανικολάου",       "Sales",        "Sales Rep",         36000, "2023-06-15"),
        (7,  "Γιώργος Ιωάννου",          "Engineering",  "Tech Lead",         72000, "2018-09-01"),
        (8,  "Αθηνά Χριστοδούλου",       "HR",           "HR Manager",        52000, "2020-01-15"),
        (9,  "Κώστας Βασιλείου",         "Engineering",  "DevOps Engineer",   60000, "2021-11-01"),
        (10, "Αναστασία Νικολάου",       "Finance",      "Financial Analyst", 50000, "2022-03-01"),
    ]
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", employees)

    # ── Table: sales ─────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            quantity INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            region TEXT NOT NULL
        )
    """)

    sales = [
        (1,  "Laptop Pro 15",     "Electronics", 1200.00, 5,  "2024-01-15", "Athens"),
        (2,  "Wireless Mouse",    "Accessories", 25.00,   50, "2024-01-18", "Thessaloniki"),
        (3,  "Office Chair",      "Furniture",   350.00,  12, "2024-02-01", "Athens"),
        (4,  "Monitor 27\"",      "Electronics", 450.00,  8,  "2024-02-10", "Patras"),
        (5,  "Keyboard Mech",     "Accessories", 80.00,   30, "2024-02-15", "Athens"),
        (6,  "Standing Desk",     "Furniture",   600.00,  6,  "2024-03-01", "Thessaloniki"),
        (7,  "Laptop Pro 15",     "Electronics", 1200.00, 3,  "2024-03-10", "Heraklion"),
        (8,  "USB-C Hub",         "Accessories", 45.00,   40, "2024-03-15", "Athens"),
        (9,  "Webcam HD",         "Electronics", 75.00,   20, "2024-04-01", "Thessaloniki"),
        (10, "Desk Lamp",         "Furniture",   55.00,   25, "2024-04-10", "Patras"),
        (11, "Laptop Pro 15",     "Electronics", 1200.00, 7,  "2024-05-01", "Athens"),
        (12, "Wireless Mouse",    "Accessories", 25.00,   60, "2024-05-15", "Heraklion"),
        (13, "Office Chair",      "Furniture",   350.00,  10, "2024-06-01", "Thessaloniki"),
        (14, "Monitor 27\"",      "Electronics", 450.00,  5,  "2024-06-20", "Athens"),
        (15, "Noise-Cancel Buds", "Electronics", 150.00,  35, "2024-07-01", "Patras"),
        (16, "Standing Desk",     "Furniture",   600.00,  4,  "2024-07-15", "Athens"),
        (17, "Keyboard Mech",     "Accessories", 80.00,   25, "2024-08-01", "Thessaloniki"),
        (18, "Laptop Pro 15",     "Electronics", 1200.00, 4,  "2024-08-20", "Athens"),
        (19, "USB-C Hub",         "Accessories", 45.00,   35, "2024-09-01", "Heraklion"),
        (20, "Webcam HD",         "Electronics", 75.00,   15, "2024-09-15", "Thessaloniki"),
    ]
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?)", sales)

    # ── Table: projects ──────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            budget REAL NOT NULL,
            status TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT
        )
    """)

    projects = [
        (1, "Website Redesign",     "Engineering", 50000,  "Completed",   "2023-06-01", "2024-01-15"),
        (2, "Mobile App v2",        "Engineering", 80000,  "In Progress", "2024-02-01", None),
        (3, "Brand Campaign 2024",  "Marketing",   35000,  "Completed",   "2024-01-15", "2024-06-30"),
        (4, "CRM Integration",      "Sales",       25000,  "In Progress", "2024-04-01", None),
        (5, "Data Pipeline",        "Engineering", 40000,  "Planning",    "2024-09-01", None),
        (6, "Employee Portal",      "HR",          20000,  "Completed",   "2023-09-01", "2024-03-15"),
    ]
    cursor.executemany("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)", projects)

    conn.commit()
    conn.close()

    print(f"✅ Sample database created at: {db_path}")
    print(f"   Tables: employees (10 rows), sales (20 rows), projects (6 rows)")


if __name__ == "__main__":
    create_sample_db()
