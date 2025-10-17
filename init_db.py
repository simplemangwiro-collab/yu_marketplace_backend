import sqlite3
from app import app
from models import db

with app.app_context():
    db.create_all()
    print("Database tables created.")

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect("marketplace.db")
cursor = conn.cursor()

# Drop tables if they exist (for clean setup)
cursor.execute("DROP TABLE IF EXISTS products")
cursor.execute("DROP TABLE IF EXISTS messages")

# Create the products table
cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    price REAL NOT NULL,
    seller TEXT
)
''')

# Create the messages table
cursor.execute('''
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    receiver TEXT NOT NULL,
    item_id INTEGER,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Insert sample products
sample_items = [
    ("Notebook", 3.99, "alice"),
    ("Pen", 1.49, "bob"),
    ("Backpack", 25.00, "charlie")
]

cursor.executemany("INSERT INTO products (product_name, price, seller) VALUES (?, ?, ?)", sample_items)

# Save and close
conn.commit()
conn.close()

print("Database initialized with sample products and messaging support.")
