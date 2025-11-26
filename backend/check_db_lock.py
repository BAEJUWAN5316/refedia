from database import SessionLocal
from sqlalchemy import text
import time

def check_lock():
    print("🔓 Checking DB lock...")
    db = SessionLocal()
    try:
        # Try to write something
        print("📝 Attempting to write...")
        start = time.time()
        db.execute(text("CREATE TABLE IF NOT EXISTS lock_test (id INTEGER PRIMARY KEY)"))
        db.execute(text("INSERT INTO lock_test DEFAULT VALUES"))
        db.commit()
        print(f"✅ Write successful in {time.time() - start:.2f}s")
        
        # Clean up
        db.execute(text("DROP TABLE lock_test"))
        db.commit()
    except Exception as e:
        print(f"❌ DB Write failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_lock()
