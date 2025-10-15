import sqlite3

conn = sqlite3.connect("marketplace.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
    print("✅ 'image_url' column added successfully.")
except sqlite3.OperationalError as e:
    print("⚠️ Column may already exist or error occurred:", e)

conn.commit()
conn.close()
