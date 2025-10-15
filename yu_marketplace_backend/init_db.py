import sqlite3

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect("marketplace.db")
cursor = conn.cursor()

# Drop the table if it exists (for clean setup)
cursor.execute("DROP TABLE IF EXISTS products")

# Create the products table
cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    price REAL NOT NULL
)
''')

# Insert sample data
sample_items = [
    ("Notebook", 3.99),
    ("Pen", 1.49),
    ("Backpack", 25.00)
]

cursor.executemany("INSERT INTO products (product_name, price) VALUES (?, ?)", sample_items)

# Save and close
conn.commit()
conn.close()

print("Database initialized with sample products.")
