import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_RrZHU9sTO4Wb@ep-super-glitter-ag00m0lo-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

operations = [
    ("Drop activity_follows", "DROP TABLE IF EXISTS activity_follows CASCADE"),
    ("Drop activity_likes_item", "DROP TABLE IF EXISTS activity_likes_item CASCADE"),
    ("Drop activity_likes_review", "DROP TABLE IF EXISTS activity_likes_review CASCADE"),
    ("Drop activity_list_adds", "DROP TABLE IF EXISTS activity_list_adds CASCADE"),
    ("Drop activity_ratings", "DROP TABLE IF EXISTS activity_ratings CASCADE"),
    ("Drop activity_reviews", "DROP TABLE IF EXISTS activity_reviews CASCADE"),
    ("Drop activities", "DROP TABLE IF EXISTS activities CASCADE"),
    ("Create activities", """CREATE TABLE activities (
        activity_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        activity_type VARCHAR(50) NOT NULL,
        item_id INTEGER REFERENCES items(item_id) ON DELETE CASCADE,
        review_id INTEGER REFERENCES reviews(review_id) ON DELETE CASCADE,
        list_id INTEGER REFERENCES lists(list_id) ON DELETE CASCADE,
        related_user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""),
]

print("Applying database changes...")
print("="*60)

with engine.begin() as conn:
    for name, sql in operations:
        try:
            conn.execute(text(sql))
            print(f"[OK] {name}")
        except Exception as e:
            print(f"[ERROR] {name}: {str(e)[:100]}")

print("\n" + "="*60)
print("[SUCCESS] Database cleanup completed!")
