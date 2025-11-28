import sqlite3

def check_and_fix_schema():
    conn = sqlite3.connect('refedia.db')
    cursor = conn.cursor()
    
    # Check columns in posts table
    cursor.execute("PRAGMA table_info(posts)")
    columns = [info[1] for info in cursor.fetchall()]
    
    print(f"Current columns: {columns}")
    
    if 'view_count' not in columns:
        print("⚠️ 'view_count' column missing. Adding it...")
        try:
            cursor.execute("ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0")
            conn.commit()
            print("✅ 'view_count' column added successfully.")
        except Exception as e:
            print(f"❌ Failed to add column: {e}")
    else:
        print("✅ 'view_count' column already exists.")
        
    conn.close()

if __name__ == "__main__":
    check_and_fix_schema()
