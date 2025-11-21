#!/usr/bin/env python
import requests

print("=" * 60)
print("EXTERNAL API TEST - HARRY SEARCH")
print("=" * 60)

# Test Movie API
print("\n🎬 TMDB Film API Testi:")
url = 'http://127.0.0.1:8000/external/search?type=movie&query=harry'
try:
    resp = requests.get(url, timeout=5)
    print(f'   Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'   Sonuç: {len(data)} film bulundu')
        for idx, item in enumerate(data[:3]):
            print(f'     [{idx+1}] {item.get("title")} ({item.get("year")})')
    else:
        print(f'   Error: {resp.text[:200]}')
except Exception as e:
    print(f'   Hata: {e}')

# Test Book API
print("\n📖 Google Books API Testi:")
url = 'http://127.0.0.1:8000/external/search?type=book&query=harry'
try:
    resp = requests.get(url, timeout=5)
    print(f'   Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'   Sonuç: {len(data)} kitap bulundu')
        for idx, item in enumerate(data[:3]):
            print(f'     [{idx+1}] {item.get("title")} (Yazar: {item.get("authors")})')
    else:
        print(f'   Error: {resp.text[:200]}')
except Exception as e:
    print(f'   Hata: {e}')

# Test Database Search
print("\n📚 Veritabanı Arama Testi:")
url = 'http://127.0.0.1:8000/items/search?q=harry'
try:
    resp = requests.get(url, timeout=5)
    print(f'   Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'   Sonuç: {len(data)} sonuç bulundu')
        for idx, item in enumerate(data):
            print(f'     [{idx+1}] ID:{item.get("item_id")} - {item.get("title")}')
    else:
        print(f'   Error: {resp.text[:200]}')
except Exception as e:
    print(f'   Hata: {e}')

print("\n" + "=" * 60)
