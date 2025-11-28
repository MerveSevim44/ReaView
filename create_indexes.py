import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_RrZHU9sTO4Wb@ep-super-glitter-ag00m0lo-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

indexes = [
    ("idx_activities_user_id", "CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id)"),
    ("idx_activities_created", "CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at DESC)"),
    ("idx_activities_type", "CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type)"),
    ("idx_activities_user_created", "CREATE INDEX IF NOT EXISTS idx_activities_user_created ON activities(user_id, created_at DESC)"),
    ("idx_activities_item", "CREATE INDEX IF NOT EXISTS idx_activities_item_id ON activities(item_id)"),
    ("idx_activities_review", "CREATE INDEX IF NOT EXISTS idx_activities_review_id ON activities(review_id)"),
    ("idx_activities_related", "CREATE INDEX IF NOT EXISTS idx_activities_related_user ON activities(related_user_id)"),
    ("idx_reviews_user_created", "CREATE INDEX IF NOT EXISTS idx_reviews_user_created ON reviews(user_id, created_at DESC)"),
    ("idx_ratings_user_created", "CREATE INDEX IF NOT EXISTS idx_ratings_user_created ON ratings(user_id, created_at DESC)"),
    ("idx_follows_follower", "CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id)"),
    ("idx_follows_followee", "CREATE INDEX IF NOT EXISTS idx_follows_followee ON follows(followee_id)"),
    ("idx_review_likes_review", "CREATE INDEX IF NOT EXISTS idx_review_likes_review ON review_likes(review_id)"),
    ("idx_item_likes_item", "CREATE INDEX IF NOT EXISTS idx_item_likes_item ON item_likes(item_id)"),
    ("idx_user_library_user", "CREATE INDEX IF NOT EXISTS idx_user_library_user ON user_library(user_id, status)"),
]

print("Creating indexes for Feed optimization...")
print("="*60)

with engine.begin() as conn:
    for name, sql in indexes:
        try:
            conn.execute(text(sql))
            print(f"[OK] {name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"[SKIP] {name} (already exists)")
            else:
                print(f"[ERROR] {name}: {str(e)[:80]}")

print("\n" + "="*60)
print("[SUCCESS] Indexes created!")
