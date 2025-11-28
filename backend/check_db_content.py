import sqlite3
import os

db_path = 'refedia.db'
print(f"Checking DB at: {os.path.abspath(db_path)}")

if not os.path.exists(db_path):
    print("❌ refedia.db does not exist!")
else:
    print(f"✅ refedia.db exists. Size: {os.path.getsize(db_path)} bytes")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tables = ['users', 'posts', 'categories']
        for table in tables:
            try:
                cursor.execute(f"SELECT count(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📊 {table}: {count} rows")
            except Exception as e:
                print(f"⚠️ {table}: Error - {e}")
                
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
