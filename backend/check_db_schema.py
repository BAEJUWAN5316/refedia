from database import engine
from sqlalchemy import inspect

def check_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('posts')
    print("Columns in 'posts' table:")
    for column in columns:
        print(f" - {column['name']} ({column['type']})")

if __name__ == "__main__":
    check_schema()
