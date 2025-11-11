import requests
from fastapi import HTTPException
import os

TMDB_API_KEY = os.getenv("API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

def search_tmdb(query: str):
    """Search TMDb API for movies and return normalized results."""
    params = {"api_key": TMDB_API_KEY, "query": query, "language": "tr-TR"}
    r = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="TMDb API hatası")
    results = r.json().get("results", [])
    movies = []
    
    for m in results:
        movie = {
            "title": m.get("title", "Unknown"),
            "description": m.get("overview", ""),
            "year": int((m.get("release_date") or "0000")[:4]),
            "poster_url": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get("poster_path") else None,
            "item_type": "movie",
            "external_api_source": "tmdb",
            "genres": None,
            "director": None,
            "actors": None,
        }
        
        # Fetch movie details to get director and actors
        movie_id = m.get("id")
        if movie_id:
            try:
                details_r = requests.get(
                    f"{TMDB_BASE_URL}/movie/{movie_id}",
                    params={"api_key": TMDB_API_KEY, "language": "tr-TR"}
                )
                if details_r.status_code == 200:
                    details = details_r.json()
                    genres = [g.get("name") for g in details.get("genres", [])]
                    movie["genres"] = ", ".join(genres) if genres else None
                    
                    credits_r = requests.get(
                        f"{TMDB_BASE_URL}/movie/{movie_id}/credits",
                        params={"api_key": TMDB_API_KEY}
                    )
                    if credits_r.status_code == 200:
                        credits = credits_r.json()
                        crew = credits.get("crew", [])
                        directors = [c.get("name") for c in crew if c.get("job") == "Director"]
                        movie["director"] = directors[0] if directors else None
                        
                        cast = credits.get("cast", [])[:5]
                        actors = [c.get("name") for c in cast]
                        movie["actors"] = ", ".join(actors) if actors else None
            except Exception as e:
                print(f"Error fetching TMDb details: {e}")
        
        movies.append(movie)
    
    return movies

def search_google_books(query: str):
    """Search Google Books API and return normalized results."""
    params = {"q": query, "langRestrict": "tr", "maxResults": 10}
    r = requests.get(GOOGLE_BOOKS_URL, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="Google Books API hatası")
    
    results = r.json().get("items", [])
    books = []
    
    for b in results:
        info = b.get("volumeInfo", {})
        book = {
            "title": info.get("title", "Unknown"),
            "description": info.get("description", ""),
            "year": int(info.get("publishedDate", "0000")[:4]) if info.get("publishedDate") else None,
            "poster_url": (info.get("imageLinks") or {}).get("thumbnail"),
            "item_type": "book",
            "external_api_source": "google_books",
            "authors": ", ".join(info.get("authors", [])) if info.get("authors") else None,
            "page_count": info.get("pageCount"),
            "genres": ", ".join(info.get("categories", [])) if info.get("categories") else None,
        }
        books.append(book)
    
    return books

def search_openlibrary(query: str):
    """Search OpenLibrary API and return normalized results."""
    params = {"q": query}
    r = requests.get(OPEN_LIBRARY_URL, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="OpenLibrary API hatası")
    
    data = r.json()
    docs = data.get("docs", [])
    books = []
    
    for b in docs[:10]:
        cover_id = b.get("cover_i")
        book = {
            "title": b.get("title", "Unknown"),
            "description": "",
            "year": b.get("first_publish_year"),
            "poster_url": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None,
            "item_type": "book",
            "external_api_source": "openlibrary",
            "authors": ", ".join(b.get("author_name", [])) if b.get("author_name") else None,
            "page_count": b.get("number_of_pages_median"),
            "genres": ", ".join(b.get("subject", [])[:5]) if b.get("subject") else None,
        }
        books.append(book)
    
    return books
