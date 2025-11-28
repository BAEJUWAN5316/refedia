import sqlite3
import json
import os

DB_PATH = "refedia.db"
if not os.path.exists(DB_PATH):
    # Fallback to test.db if refedia.db doesn't exist or if app is using test.db
    if os.path.exists("test.db"):
        DB_PATH = "test.db"
    else:
        print("❌ No database file found!")
        exit(1)

print(f"🔧 Fixing database: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # 1. Check existing columns
    cursor.execute("PRAGMA table_info(posts)")
    columns = [info[1] for info in cursor.fetchall()]
    
    # 2. Add new columns if missing
    if 'primary_categories' not in columns:
        print("➕ Adding primary_categories column...")
        cursor.execute("ALTER TABLE posts ADD COLUMN primary_categories TEXT")
    
    if 'secondary_categories' not in columns:
        print("➕ Adding secondary_categories column...")
        cursor.execute("ALTER TABLE posts ADD COLUMN secondary_categories TEXT")
        
    # 3. Migrate data
    print("🔄 Migrating data...")
    cursor.execute("SELECT id, primary_category, secondary_category FROM posts")
    rows = cursor.fetchall()
    
    for row in rows:
        post_id, p_cat, s_cat = row
        
        # Convert to JSON list
        p_list = json.dumps([p_cat] if p_cat else [])
        s_list = json.dumps([s_cat] if s_cat else [])
        
        cursor.execute(
            "UPDATE posts SET primary_categories = ?, secondary_categories = ? WHERE id = ?",
            (p_list, s_list, post_id)
        )
        
    conn.commit()
    print("✅ Data migration complete.")
    
    # 4. Verify
    cursor.execute("SELECT id, primary_categories, secondary_categories FROM posts LIMIT 1")
    print(f"👀 Sample data: {cursor.fetchone()}")

except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
