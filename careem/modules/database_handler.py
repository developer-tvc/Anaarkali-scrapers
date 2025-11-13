import sqlite3
from datetime import datetime

DB_PATH = "orders.db"

def create_table_if_not_exists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id TEXT PRIMARY KEY,
                        status TEXT,
                        insert_time TEXT
                      )''')
    
    conn.commit()
    conn.close()

def get_completed_cancelled_orders():
    create_table_if_not_exists()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT order_id FROM orders WHERE status IN ('Delivered', 'Cancelled')")
    rows = cursor.fetchall()
    
    conn.close()
    
    return [row[0] for row in rows]

def insert_order_to_db(order_id, status):
    create_table_if_not_exists()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    insert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT OR REPLACE INTO orders (order_id, status, insert_time) VALUES (?, ?, ?)",
                   (order_id, status, insert_time))
    
    conn.commit()
    conn.close()
