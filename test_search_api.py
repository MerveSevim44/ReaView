#!/usr/bin/env python
import requests
import json

print("=" * 50)
print("SEARCH API TEST")
print("=" * 50)

url = "http://127.0.0.1:8000/items/search?q=harry"
resp = requests.get(url)
data = resp.json()

print(f"\n✅ API Status: {resp.status_code}")
print(f"📊 Total Results: {len(data)}\n")

for idx, item in enumerate(data):
    print(f"[{idx+1}] ID:{item.get('item_id')}, Title:{item.get('title')}, Type:{item.get('item_type')}")
    print(f"    Rating: {item.get('combined_rating')}/10")

print("\n" + "=" * 50)
print("FILTERING TEST (No filters)")
print("=" * 50)

# Simulate frontend filtering
all_results = data.copy()
filter_type = ""  # No filter
filter_year = ""  # No filter  
filter_rating = ""  # No filter

print(f"\n📊 Before filtering: {len(all_results)} items")

if filter_type:
    all_results = [item for item in all_results if item.get("item_type") == filter_type]
    print(f"📊 After type filter: {len(all_results)} items")

if filter_year:
    all_results = [item for item in all_results if item.get("year") == int(filter_year)]
    print(f"📊 After year filter: {len(all_results)} items")

if filter_rating:
    min_rating = float(filter_rating)
    all_results = [item for item in all_results if (item.get("combined_rating") or item.get("user_rating") or item.get("external_rating") or 0) >= min_rating]
    print(f"📊 After rating filter: {len(all_results)} items")

print(f"\n✅ Final Results: {len(all_results)} items\n")

for idx, item in enumerate(all_results):
    print(f"[{idx+1}] ID:{item.get('item_id')}, Title:{item.get('title')}")
