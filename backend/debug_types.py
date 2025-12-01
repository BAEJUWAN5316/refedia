import requests
import json
import sys
import os
sys.path.append(os.getcwd())
from database import SessionLocal
from db_models import Category, Post

# 1. Inspect DB directly
db = SessionLocal()
print("--- DB Inspection ---")
categories = db.query(Category).all()
print(f"Total Categories: {len(categories)}")
for c in categories:
    if not isinstance(c.id, str):
        print(f"WARNING: Category ID is not string! {c.id} ({type(c.id)})")
    # Check if ID looks like a number
    if str(c.id).isdigit():
        print(f"Category ID is numeric string: {c.id} ({c.name})")

post = db.query(Post).filter(Post.id == 26).first()
if post:
    print(f"Post 26 Genre Categories (Raw): {post.genre_categories} ({type(post.genre_categories)})")
else:
    print("Post 26 not found")

# 2. Inspect API Response
print("\n--- API Inspection ---")
try:
    response = requests.get("http://localhost:8000/api/categories")
    if response.status_code == 200:
        data = response.json()
        genres = data.get('genre', [])
        print(f"API Genres: {len(genres)}")
        for g in genres:
            if not isinstance(g['id'], str):
                 print(f"WARNING: API Category ID is not string! {g['id']} ({type(g['id'])})")
    else:
        print(f"Failed to fetch categories: {response.status_code}")
except Exception as e:
    print(f"API Request failed: {e}")
