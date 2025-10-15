import sqlite3

# Connect to your existing database
conn = sqlite3.connect("marketplace.db")
cursor = conn.cursor()

# Add 'category' column if it doesn't exist
try:
    cursor.execute("ALTER TABLE products ADD COLUMN category TEXT")
    print("✅ 'category' column added successfully.")
except sqlite3.OperationalError as e:
    print("⚠️ Column may already exist or error occurred:", e)

conn.commit()
conn.close()
