import sqlite3
import json

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute("SELECT id, primary_categories, secondary_categories FROM posts LIMIT 5")
rows = cursor.fetchall()

print("--- Category Data Check ---")
for row in rows:
    post_id, p_cat, s_cat = row
    print(f"Post {post_id}:")
    print(f"  Primary: {p_cat} (Type: {type(p_cat)})")
    print(f"  Secondary: {s_cat} (Type: {type(s_cat)})")
    
conn.close()
