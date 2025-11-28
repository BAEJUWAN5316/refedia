from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
if 'favorites' in inspector.get_table_names():
    print("✅ 'favorites' table exists.")
    columns = inspector.get_columns('favorites')
    for col in columns:
        print(f" - {col['name']} ({col['type']})")
else:
    print("❌ 'favorites' table does NOT exist.")
