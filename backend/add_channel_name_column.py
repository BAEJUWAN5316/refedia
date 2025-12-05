import sqlite3
import os

DB_FILE = "test.db"

if not os.path.exists(DB_FILE):
    print(f"❌ Database file {DB_FILE} not found!")
    exit(1)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(posts)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "channel_name" in columns:
        print("✅ Column 'channel_name' already exists.")
    else:
        print("🚧 Adding 'channel_name' column...")
        cursor.execute("ALTER TABLE posts ADD COLUMN channel_name VARCHAR")
        conn.commit()
        print("✅ Column added successfully.")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
