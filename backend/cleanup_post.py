import sys
import os
sys.path.append(os.getcwd())
from database import SessionLocal
from db_models import Post
from sqlalchemy.orm.attributes import flag_modified

db = SessionLocal()
post = db.query(Post).filter(Post.id == 26).first()
if post:
    print(f"Before: {post.genre_categories}")
    # Remove 'Genre1' and 'Genre2'
    new_genres = [g for g in post.genre_categories if g not in ['Genre1', 'Genre2']]
    # Also remove any other non-UUID strings if necessary, but let's just target the ones I added.
    # Actually, I should probably remove any string that is not a valid UUID if I want to be clean, but I don't want to delete user data.
    # I'll just remove Genre1/2.
    post.genre_categories = new_genres
    flag_modified(post, "genre_categories")
    db.commit()
    print(f"After: {post.genre_categories}")
else:
    print("Post 26 not found")
