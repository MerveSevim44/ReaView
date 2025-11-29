#!/usr/bin/env python3
"""
Debug script to check activities table data
Aktivite tablosundaki veri debug'ı
"""
import sys
sys.path.insert(0, '/Users/User/ReaView/backend')

from app.database import SessionLocal
from app import models
from sqlalchemy import text

db = SessionLocal()

print("\n" + "="*80)
print("🔍 ACTIVITIES TABLE DEBUG")
print("="*80 + "\n")

# Get all activities
activities = db.query(models.Activity).all()
print(f"📊 Total activities: {len(activities)}\n")

for activity in activities[:10]:  # First 10
    print(f"Activity ID: {activity.activity_id}")
    print(f"  Type: {activity.activity_type}")
    print(f"  User ID: {activity.user_id}")
    print(f"  Item ID: {activity.item_id}")
    print(f"  Review ID: {activity.review_id}")
    print(f"  List ID: {activity.list_id}")
    print(f"  Created: {activity.created_at}")
    
    # Try to fetch item
    if activity.item_id:
        item = db.query(models.Item).filter(models.Item.item_id == activity.item_id).first()
        if item:
            print(f"  ✅ Item: {item.title} ({item.item_id})")
        else:
            print(f"  ❌ Item {activity.item_id} NOT FOUND!")
    else:
        print(f"  ⚠️ Item ID is NULL")
    
    # Try to fetch review
    if activity.review_id:
        review = db.query(models.Review).filter(models.Review.review_id == activity.review_id).first()
        if review:
            print(f"  ✅ Review: {review.review_id} - {review.review_text[:50]}...")
        else:
            print(f"  ❌ Review {activity.review_id} NOT FOUND!")
    
    print()

# Check feed query
print("\n" + "="*80)
print("🔍 FEED QUERY DEBUG (for user_id=2)")
print("="*80 + "\n")

# Assuming user 2 exists and has followers
user_id = 2
query = text("""
    SELECT 
        a.activity_id,
        a.user_id,
        u.username,
        a.activity_type,
        a.item_id,
        i.title,
        i.poster_url,
        r.review_text,
        rat.score as rating_score
    FROM activities a
    JOIN users u ON u.user_id = a.user_id
    LEFT JOIN items i ON i.item_id = a.item_id
    LEFT JOIN reviews r ON r.review_id = a.review_id
    LEFT JOIN ratings rat ON rat.user_id = a.user_id AND rat.item_id = a.item_id
    WHERE a.activity_type IN ('review', 'rating')
    LIMIT 5
""")

result = db.execute(query).fetchall()
print(f"Query result count: {len(result)}\n")

for row in result:
    print(f"Activity {row[0]}: {row[3]} by {row[2]}")
    print(f"  Item ID: {row[4]}")
    print(f"  Title: {row[5]}")
    print(f"  Poster: {row[6][:50] if row[6] else 'NULL'}...")
    print(f"  Review: {row[7][:50] if row[7] else 'NULL'}...")
    print(f"  Rating: {row[8]}")
    print()

db.close()
