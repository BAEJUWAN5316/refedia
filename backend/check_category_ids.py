
from database import SessionLocal
from db_models import Category

def check_category_ids():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        print(f"Total categories: {len(categories)}")
        if categories:
            first_cat = categories[0]
            print(f"Sample Category: ID={first_cat.id} (Type: {type(first_cat.id)}), Name={first_cat.name}")
            
            # Check if all IDs are strings
            all_strings = all(isinstance(c.id, str) for c in categories)
            print(f"All IDs are strings: {all_strings}")
            
            print("\n🔍 Sample Category Names:")
            for c in categories[:20]:
                print(f"   - {c.name} ({c.type})")

    finally:
        db.close()

if __name__ == "__main__":
    check_category_ids()
