import sqlite3
from datetime import datetime

DB_FILE = "orders.db"

def create_table():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                status TEXT,
                insert_time TEXT
            )
        """)
        conn.commit()

def get_completed_cancelled_orders():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT order_id FROM orders WHERE status IN ('completed', 'cancelled')")
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def add_order_to_db(order_id, status):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        insert_time = datetime.now().isoformat()
        cursor.execute("INSERT OR IGNORE INTO orders (order_id, status, insert_time) VALUES (?, ?, ?)", 
                       (order_id, status, insert_time))
        conn.commit()
