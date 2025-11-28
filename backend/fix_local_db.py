import sqlite3
import json
import os
from sqlalchemy import inspect, create_engine

# Use test.db by default as that seems to be what the app uses locally
DB_PATH = "test.db"
if not os.path.exists(DB_PATH):
    print("❌ No test.db file found!")
    if os.path.exists("refedia.db"):
        DB_PATH = "refedia.db"
    else:
        # Create empty test.db if needed, but for now just exit
        print("Creating new test.db...")
        DB_PATH = "test.db"

print(f"🔧 Fixing database: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Check existing columns in posts
    cursor.execute("PRAGMA table_info(posts)")
    columns_info = cursor.fetchall()
    columns = [info[1] for info in columns_info]
    
    if 'primary_categories' not in columns:
        print("➕ Adding primary_categories column...")
        cursor.execute("ALTER TABLE posts ADD COLUMN primary_categories TEXT")
    
    if 'secondary_categories' not in columns:
        print("➕ Adding secondary_categories column...")
        cursor.execute("ALTER TABLE posts ADD COLUMN secondary_categories TEXT")

    if 'view_count' not in columns:
        print("➕ Adding view_count column...")
        cursor.execute("ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0")

    if 'author_id' in columns and 'user_id' not in columns:
        print("🔄 Renaming author_id to user_id...")
        cursor.execute("ALTER TABLE posts RENAME COLUMN author_id TO user_id")

    # Check favorites table schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='favorites'")
    favorites_exists = cursor.fetchone()
    
    if favorites_exists:
        cursor.execute("PRAGMA table_info(favorites)")
        columns_info = cursor.fetchall()
        column_names = [info[1] for info in columns_info]
        
        if 'id' not in column_names:
            print("⚠️ favorites table missing 'id' column. Recreating...")
            cursor.execute("DROP TABLE favorites")
            favorites_exists = None
        
    if not favorites_exists:
        print("➕ Creating favorites table...")
        cursor.execute("""
            CREATE TABLE favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                post_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(post_id) REFERENCES posts(id)
            )
        """)
        
    print("🔄 Migrating data...")
    cursor.execute("SELECT id, primary_category, secondary_category FROM posts")
    rows = cursor.fetchall()
    
    for row in rows:
        post_id, p_cat, s_cat = row
        # Skip if columns don't exist in row (should exist if query succeeded)
        # But wait, primary_category column might not exist if we renamed/deleted it?
        # The original schema had primary_category (singular).
        # We added plural columns.
        # We need to migrate data from singular to plural if singular exists.
        pass

    # Actually, the migration logic depends on whether 'primary_category' column exists.
    # Let's check if 'primary_category' exists in columns
    if 'primary_category' in columns:
        print("Migrating from singular to plural categories...")
        cursor.execute("SELECT id, primary_category, secondary_category FROM posts")
        rows = cursor.fetchall()
        for row in rows:
            post_id, p_cat, s_cat = row
            p_list = json.dumps([p_cat] if p_cat else [])
            s_list = json.dumps([s_cat] if s_cat else [])
            cursor.execute(
                "UPDATE posts SET primary_categories = ?, secondary_categories = ? WHERE id = ?",
                (p_list, s_list, post_id)
            )

    conn.commit()
    print("✅ Data migration complete.")

except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
