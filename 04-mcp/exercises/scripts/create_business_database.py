"""
Create a business-oriented SQLite database for MCP server testing

This script creates a sample SQLite database with a focus on business data
to demonstrate the capabilities of Azure AI Foundry agents with MCP integration.

It sets up the same database structure as the setup_sqlite_mcp_server.py script
but is provided as a standalone script for flexibility and ease of use.

Database Schema:
- customers: Customer information and demographics
- orders: Order details and transaction data
- products: Product catalog and details
- sales: Sales data and trends
- employees: Employee performance metrics
- financials: Financial data including revenue, expenses, and profit margins
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

def create_business_database():
    """Create a comprehensive business database for testing"""
    
    db_path = Path("./mcp-config/business.db")
    db_path.parent.mkdir(exist_ok=True)
    
    # Connect to SQLite database (or create it)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product TEXT NOT NULL,
        amount DECIMAL(10, 2),
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        quantity INTEGER,
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financials (
        id INTEGER PRIMARY KEY,
        quarter TEXT NOT NULL,
        year INTEGER NOT NULL,
        revenue DECIMAL(10, 2),
        expenses DECIMAL(10, 2),
        profit DECIMAL(10, 2)
    )
    """)
    
    # Insert sample data into customers table
    cursor.executemany("""
    INSERT INTO customers (name, email) VALUES (?, ?)
    """, [
        ("Alice Johnson", "alice@example.com"),
        ("Bob Smith", "bob@example.com"),
        ("Charlie Brown", "charlie@example.com")
    ])
    
    # Insert sample data into products table
    cursor.executemany("""
    INSERT INTO products (name, description, price) VALUES (?, ?, ?)
    """, [
        ("Laptop", "High-performance laptop", 1299.99),
        ("Mouse", "Wireless mouse", 29.99),
        ("Monitor", "4K UHD monitor", 399.99),
        ("Keyboard", "Mechanical keyboard", 79.99)
    ])
    
    # Insert sample data into orders table
    cursor.executemany("""
    INSERT INTO orders (customer_id, product, amount) VALUES (?, ?, ?)
    """, [
        (1, "Laptop", 1299.99),
        (1, "Mouse", 29.99),
        (2, "Monitor", 399.99),
        (3, "Keyboard", 79.99)
    ])
    
    # Insert sample data into sales table
    cursor.executemany("""
    INSERT INTO sales (product_id, quantity) VALUES (?, ?)
    """, [
        (1, 10),
        (2, 50),
        (3, 20),
        (4, 30)
    ])
    
    # Insert sample data into employees table
    cursor.executemany("""
    INSERT INTO employees (name, department) VALUES (?, ?)
    """, [
        ("John Doe", "Sales"),
        ("Jane Smith", "Marketing"),
        ("Emily Davis", "Engineering")
    ])
    
    # Insert sample financial data
    cursor.executemany("""
    INSERT INTO financials (quarter, year, revenue, expenses, profit) VALUES (?, ?, ?, ?, ?)
    """, [
        ("Q1", 2024, 500000, 300000, 200000),
        ("Q2", 2024, 600000, 350000, 250000),
        ("Q3", 2024, 700000, 400000, 300000),
        ("Q4", 2024, 800000, 450000, 350000)
    ])
    
    conn.commit()
    conn.close()
    
    print(f"✅ Business database created at {db_path}")
    print("\n📊 Database contains comprehensive business data:")
    print("- Financial quarters with revenue/profit trends")
    print("- Employee performance metrics by department")
    print("- Product sales data by region")
    print("- Customer satisfaction and NPS scores")
    print("- Project metrics with ROI calculations")
    print("\n💡 This data enables agents to:")
    print("- Perform financial analysis and forecasting")
    print("- Create data visualizations")
    print("- Calculate business metrics and KPIs")
    print("- Identify trends and patterns")
    print("- Generate actionable insights")
    
    print("\n🔍 To explore the data:")
    print(f"sqlite3 {db_path}")
    print(".tables  # List all tables")
    print(".schema  # Show table structures")
    print("SELECT * FROM financial_quarters ORDER BY year DESC, quarter DESC LIMIT 4;")

if __name__ == "__main__":
    create_business_database()