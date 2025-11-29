#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/User/ReaView/backend')

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("\n📚 REVIEWS TABLE CHECK\n")

# Check reviews that don't have item_id
reviews_without_item = db.query(models.Review).filter(models.Review.item_id == None).all()
print(f"Reviews without item_id: {len(reviews_without_item)}")

for r in reviews_without_item[:5]:
    print(f"\n  Review {r.review_id}: {r.review_text[:50]}")
    print(f"  - user_id: {r.user_id}")
    print(f"  - item_id: {r.item_id}")
    print(f"  - source_id: {r.source_id}")

db.close()
