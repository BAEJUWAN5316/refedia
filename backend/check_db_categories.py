import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Category, Base

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load env (though app_main uses defaults if missing)
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
print(f"Connecting to: {DATABASE_URL}")

# Force UTF-8 for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    categories = db.query(Category).all()
    
    categories_structure = {
        "industry": [{"id": c.id, "name": c.name} for c in categories if c.type == "industry"],
        "genre": [{"id": c.id, "name": c.name} for c in categories if c.type == "genre"],
        "cast": [{"id": c.id, "name": c.name} for c in categories if c.type == "cast"],
        "mood": [{"id": c.id, "name": c.name} for c in categories if c.type == "mood"],
        "editing": [{"id": c.id, "name": c.name} for c in categories if c.type == "editing"],
    }
    
    with open("db_check_result.txt", "w", encoding="utf-8") as f:
        f.write(f"DEBUG: Fetched {len(categories)} categories from DB.\n")
        f.write(f"DEBUG: Structure sizes -> Industry: {len(categories_structure['industry'])}, Genre: {len(categories_structure['genre'])}\n")
        
        if len(categories) > 0:
            f.write("Sample Industry Categories:\n")
            for c in categories_structure['industry'][:5]:
                f.write(f" - {c['name']} (ID: {c['id']})\n")
                
    print("Done writing to db_check_result.txt")

except Exception as e:
    print(f"ERROR: {e}")
    with open("db_check_result.txt", "w", encoding="utf-8") as f:
        f.write(f"ERROR: {e}\n")
finally:
    db.close()
