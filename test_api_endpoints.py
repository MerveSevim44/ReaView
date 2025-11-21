#!/usr/bin/env python3
"""
Test API endpoints for comments functionality
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

def test_api_comments():
    """Test API comments endpoints"""
    print("\n" + "="*60)
    print("API COMMENTS ENDPOINT TEST")
    print("="*60)
    
    # Test 1: TMDB Film Yorumları
    source_id_tmdb = "tmdb_550"
    print(f"\n1️⃣  Testing TMDB Comments: {source_id_tmdb}")
    try:
        response = requests.get(f"{API_BASE}/items/api/comments/{source_id_tmdb}")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Google Books Kitap Yorumları
    source_id_book = "google_books_isbn123"
    print(f"\n2️⃣  Testing Google Books Comments: {source_id_book}")
    try:
        response = requests.get(f"{API_BASE}/items/api/comments/{source_id_book}")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: DB Items Comments
    print(f"\n3️⃣  Testing DB Item Comments: /items/1/comments")
    try:
        response = requests.get(f"{API_BASE}/items/1/comments")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response count: {len(data)} comments")
        if data:
            print(f"First comment: {json.dumps(data[0], indent=2, ensure_ascii=False, default=str)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Add API Comment
    print(f"\n4️⃣  Testing Add API Comment: POST /items/api/comments/{source_id_tmdb}")
    try:
        comment_data = {
            "user_id": "test_user",
            "review_text": "Test yorum metni",
            "rating": 8
        }
        response = requests.post(
            f"{API_BASE}/items/api/comments/{source_id_tmdb}",
            json=comment_data
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_comments()
