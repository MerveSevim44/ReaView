import requests
from fastapi import HTTPException
import os
TMDB_API_KEY = os.getenv("API_KEY")  # kendi API key’in
TMDB_BASE_URL = "https://api.themoviedb.org/3"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

def search_tmdb(query: str):
    params = {"api_key": TMDB_API_KEY, "query": query, "language": "tr-TR"}
    r = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="TMDb API hatası")
    results = r.json().get("results", [])
    movies = []
    for m in results:
        movies.append({
            "title": m.get("title"),
            "description": m.get("overview"),
            "year": (m.get("release_date") or "0000")[:4],
            "poster_url": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get("poster_path") else None,
            "item_type": "movie"
        })
    return movies

def search_google_books(query: str):
    params = {"q": query, "langRestrict": "tr", "maxResults": 10}
    r = requests.get(GOOGLE_BOOKS_URL, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="Google Books API hatası")
    results = r.json().get("items", [])
    books = []
    for b in results:
        info = b.get("volumeInfo", {})
        books.append({
            "title": info.get("title"),
            "description": info.get("description"),
            "year": info.get("publishedDate", "N/A")[:4],
            "poster_url": (info.get("imageLinks") or {}).get("thumbnail"),
            "item_type": "book"
        })
    return books

def search_openlibrary(query: str):
    params = {"q": query}
    r = requests.get(OPEN_LIBRARY_URL, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="OpenLibrary API hatası")
    data = r.json()
    docs = data.get("docs", [])
    books = []
    for b in docs[:10]:
        cover_id = b.get("cover_i")
        books.append({
            "title": b.get("title"),
            "description": " - ",
            "year": b.get("first_publish_year"),
            "poster_url": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None,
            "item_type": "book"
        })
    return books
