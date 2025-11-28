import sqlite3
import json

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute("SELECT id, primary_categories, secondary_categories FROM posts")
rows = cursor.fetchall()

print("🔄 Fixing double-encoded JSON...")
count = 0
for row in rows:
    post_id, p_cat, s_cat = row
    
    try:
        # Check if it's double encoded
        # Example bad: '["[\"id\"]"]' -> loads to list containing string '["id"]'
        # Example good: '["id"]' -> loads to list containing string 'id'
        
        p_list = json.loads(p_cat) if p_cat else []
        s_list = json.loads(s_cat) if s_cat else []
        
        needs_update = False
        
        # Fix Primary
        if isinstance(p_list, list) and len(p_list) > 0 and isinstance(p_list[0], str):
            try:
                # Try to decode the inner string
                inner = json.loads(p_list[0])
                if isinstance(inner, list):
                    p_list = inner
                    needs_update = True
            except:
                pass
                
        # Fix Secondary
        if isinstance(s_list, list) and len(s_list) > 0 and isinstance(s_list[0], str):
            try:
                inner = json.loads(s_list[0])
                if isinstance(inner, list):
                    s_list = inner
                    needs_update = True
            except:
                pass
                
        if needs_update:
            cursor.execute(
                "UPDATE posts SET primary_categories = ?, secondary_categories = ? WHERE id = ?",
                (json.dumps(p_list), json.dumps(s_list), post_id)
            )
            count += 1
            
    except Exception as e:
        print(f"Error processing post {post_id}: {e}")

conn.commit()
print(f"✅ Fixed {count} posts.")
conn.close()
