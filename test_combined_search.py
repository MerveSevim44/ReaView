#!/usr/bin/env python
import requests
import json

print("=" * 70)
print("COMBINED SEARCH TEST - HARRY")
print("=" * 70)

# Veritabanı
print("\n📚 1. Veritabanı Araması:")
db_url = 'http://127.0.0.1:8000/items/search?q=harry'
try:
    resp = requests.get(db_url, timeout=5)
    db_results = resp.json() if resp.status_code == 200 else []
    print(f"   Status: {resp.status_code}, Sonuç: {len(db_results)}")
    for item in db_results:
        print(f"   - {item.get('title')} (ID: {item.get('item_id')})")
except Exception as e:
    print(f"   Hata: {e}")
    db_results = []

# External API - Filmler
print("\n🎬 2. External API Filmler:")
movie_url = 'http://127.0.0.1:8000/external/search?type=movie&query=harry'
try:
    resp = requests.get(movie_url, timeout=5)
    movies = resp.json() if resp.status_code == 200 else []
    print(f"   Status: {resp.status_code}, Sonuç: {len(movies)}")
    for item in movies[:3]:
        print(f"   - {item.get('title')} ({item.get('year')})")
    if len(movies) > 3:
        print(f"   ... ve {len(movies) - 3} tane daha")
except Exception as e:
    print(f"   Hata: {e}")
    movies = []

# External API - Kitaplar
print("\n📖 3. External API Kitaplar:")
book_url = 'http://127.0.0.1:8000/external/search?type=book&query=harry'
try:
    resp = requests.get(book_url, timeout=5)
    books = resp.json() if resp.status_code == 200 else []
    print(f"   Status: {resp.status_code}, Sonuç: {len(books)}")
    for item in books[:3]:
        print(f"   - {item.get('title')} ({item.get('authors')})")
    if len(books) > 3:
        print(f"   ... ve {len(books) - 3} tane daha")
except Exception as e:
    print(f"   Hata: {e}")
    books = []

# Birleştir
print("\n" + "=" * 70)
print("🔀 SONUÇLAR BİRLEŞTİRİLİYOR")
print("=" * 70)

all_results = db_results + movies + books
print(f"\nBirleştirilmiş Toplam: {len(all_results)} sonuç")

# Duplikat kaldır
print("\n🔍 Duplikatlara bakılıyor...")
seen = set()
unique_results = []
dup_count = 0

for item in all_results:
    key = (item.get('title') or '').lower()
    if key in seen:
        print(f"   ❌ Duplikat: '{item.get('title')}'")
        dup_count += 1
    else:
        seen.add(key)
        unique_results.append(item)

print(f"\n✅ Duplikat Kaldırıldı: {dup_count} sonuç")
print(f"📊 Nihai Toplam: {len(unique_results)} benzersiz sonuç")

print("\n" + "=" * 70)
print("ÖZETİ:")
print(f"  - Veritabanı: {len(db_results)} sonuç")
print(f"  - Filmler: {len(movies)} sonuç")
print(f"  - Kitaplar: {len(books)} sonuç")
print(f"  - Toplam Birleştirilmiş: {len(all_results)} sonuç")
print(f"  - Duplikat: {dup_count} sonuç")
print(f"  - ✅ FINAL: {len(unique_results)} benzersiz sonuç")
print("=" * 70)
