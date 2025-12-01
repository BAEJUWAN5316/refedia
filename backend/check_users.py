from sqlalchemy import create_engine, text
import os

db_path = "test.db"
if not os.path.exists(db_path):
    print(f"❌ {db_path} does not exist.")
else:
    print(f"✅ {db_path} exists.")
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, email, name, is_admin FROM users"))
            users = result.fetchall()
            print(f"Found {len(users)} users:")
            for u in users:
                print(u)
    except Exception as e:
        print(f"❌ Error reading DB: {e}")
