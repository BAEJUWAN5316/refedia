from database import SessionLocal
from db_models import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f"User: {u.email}, Admin: {u.is_admin}, Approved: {u.is_approved}")
db.close()
