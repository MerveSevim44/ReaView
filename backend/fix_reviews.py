#!/usr/bin/env python3
"""
Fix old reviews without item_id
Eski review'ları item_id ile eşleştir
"""
import sys
sys.path.insert(0, '/Users/User/ReaView/backend')

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("\n🔧 FIXING REVIEWS WITHOUT ITEM_ID\n")

# Find reviews without item_id but with source_id
reviews_to_fix = db.query(models.Review).filter(
    models.Review.item_id == None,
    models.Review.source_id != None
).all()

print(f"Found {len(reviews_to_fix)} reviews to fix\n")

for review in reviews_to_fix:
    # Find item with matching external_api_id
    item = db.query(models.Item).filter(
        models.Item.external_api_id == review.source_id
    ).first()
    
    if item:
        print(f"✅ Review {review.review_id}: Linking to Item {item.item_id} ({item.title})")
        review.item_id = item.item_id
    else:
        print(f"❌ Review {review.review_id}: No item found for {review.source_id}")

db.commit()
print("\n✅ Fix complete!")

# Now update activities table
print("\n🔧 UPDATING ACTIVITIES TABLE\n")

activities_to_fix = db.query(models.Activity).filter(
    models.Activity.item_id == None,
    models.Activity.review_id != None
).all()

print(f"Found {len(activities_to_fix)} activities to fix\n")

for activity in activities_to_fix:
    # Get review and find its item_id
    review = db.query(models.Review).filter(
        models.Review.review_id == activity.review_id
    ).first()
    
    if review and review.item_id:
        print(f"✅ Activity {activity.activity_id}: Linking to Item {review.item_id}")
        activity.item_id = review.item_id
    else:
        print(f"❌ Activity {activity.activity_id}: Review has no item_id")

db.commit()
print("\n✅ Activities fix complete!")

db.close()
