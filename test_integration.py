#!/usr/bin/env python
import requests
import json

print("=" * 80)
print("🔍 EXPLORE + ITEMS.HTML ENTEGRASİON TESTİ")
print("=" * 80)

# Test Scenario 1: Database Item
print("\n📚 TEST 1: Veritabanı İçeriği (item_id ile)")
print("-" * 80)
url = "http://127.0.0.1:8000/items/1"
try:
    resp = requests.get(url)
    item = resp.json()
    print(f"✅ Status: {resp.status_code}")
    print(f"   Title: {item.get('title')}")
    print(f"   item_id: {item.get('item_id')}")
    print(f"   Rating: {item.get('combined_rating')}/10")
    print(f"\n   Link: items.html?id={item.get('item_id')}")
except Exception as e:
    print(f"❌ Hata: {e}")

# Test Scenario 2: External API Item
print("\n\n🎬 TEST 2: External API İçeriği (API verisi ile)")
print("-" * 80)
url = "http://127.0.0.1:8000/external/search?type=movie&query=harry"
try:
    resp = requests.get(url)
    movies = resp.json()
    if movies:
        item = movies[0]
        print(f"✅ Status: {resp.status_code}")
        print(f"   Title: {item.get('title')}")
        print(f"   item_id: {item.get('item_id')} (Yok!)")
        print(f"   Year: {item.get('year')}")
        
        # Simulate what would be sent to items.html
        encoded = json.dumps(item)
        print(f"\n   Link: items.html?id={encoded[:100]}...&source=api")
        print(f"\n   ✨ API Verisi (JSON):")
        print(f"   {json.dumps(item, indent=2, ensure_ascii=False)[:300]}...")
except Exception as e:
    print(f"❌ Hata: {e}")

# Test Scenario 3: Search Results Combination
print("\n\n🔀 TEST 3: Arama Sonuçları Kombinasyonu")
print("-" * 80)
try:
    # DB Search
    db_url = "http://127.0.0.1:8000/items/search?q=harry"
    db_resp = requests.get(db_url)
    db_items = db_resp.json()
    print(f"📚 Veritabanı: {len(db_items)} sonuç")
    for item in db_items:
        print(f"   ✅ {item.get('title')} (item_id: {item.get('item_id')})")
    
    # API Search
    api_url = "http://127.0.0.1:8000/external/search?type=book&query=harry"
    api_resp = requests.get(api_url)
    api_items = api_resp.json()
    print(f"\n📖 Google Books API: {len(api_items)} sonuç")
    for idx, item in enumerate(api_items[:3]):
        print(f"   🔗 {item.get('title')} (item_id: {item.get('item_id')})")
    if len(api_items) > 3:
        print(f"   ... ve {len(api_items) - 3} tane daha")
    
    # Combined
    all_items = db_items + api_items
    print(f"\n🎯 Toplam: {len(all_items)} sonuç")
    
except Exception as e:
    print(f"❌ Hata: {e}")

print("\n" + "=" * 80)
print("✅ TEST TAMAMLANDI")
print("=" * 80)
