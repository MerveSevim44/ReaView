import requests
from fastapi import HTTPException
import os

TMDB_API_KEY = os.getenv("API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

def search_tmdb(query: str):
    """Search TMDb API for movies and return normalized results."""
    # Eğer "popular" sorgusu ise, popüler filmler endpoint'ini kullan
    if query.lower() == "popular":
        params = {"api_key": TMDB_API_KEY, "language": "tr-TR", "page": 1}
        r = requests.get(f"{TMDB_BASE_URL}/movie/popular", params=params)
    else:
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
            "external_api_id": str(m.get("id", "")),
            "external_rating": round(m.get("vote_average", 0), 1),  # TMDB: 0-10
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
        # Google Books rating: 0-5, ölçeğini 0-10'a çıkar
        gb_rating = info.get("averageRating", 0)
        external_rating = round(gb_rating * 2, 1) if gb_rating else 0
        
        book = {
            "title": info.get("title", "Unknown"),
            "description": info.get("description", ""),
            "year": int(info.get("publishedDate", "0000")[:4]) if info.get("publishedDate") else None,
            "poster_url": (info.get("imageLinks") or {}).get("thumbnail"),
            "item_type": "book",
            "external_api_source": "google_books",
            "external_api_id": b.get("id", ""),
            "external_rating": external_rating,  # Scaled to 0-10
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
        # OpenLibrary rating: 0-5, ölçeğini 0-10'a çıkar
        ol_rating = b.get("ratings_average", 0)
        external_rating = round(ol_rating * 2, 1) if ol_rating else 0
        
        cover_id = b.get("cover_i")
        book = {
            "title": b.get("title", "Unknown"),
            "description": "",
            "year": b.get("first_publish_year"),
            "poster_url": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None,
            "item_type": "book",
            "external_api_source": "openlibrary",
            "external_api_id": b.get("key", ""),
            "external_rating": external_rating,  # Scaled to 0-10
            "authors": ", ".join(b.get("author_name", [])) if b.get("author_name") else None,
            "page_count": b.get("number_of_pages_median"),
            "genres": ", ".join(b.get("subject", [])[:5]) if b.get("subject") else None,
        }
        books.append(book)
    
    return books


def get_tmdb_reviews(movie_id: str):
    """Fetch reviews/comments from TMDB API for a specific movie."""
    try:
        params = {"api_key": TMDB_API_KEY, "language": "tr-TR"}
        r = requests.get(f"{TMDB_BASE_URL}/movie/{movie_id}/reviews", params=params)
        
        if r.status_code != 200:
            return []
        
        results = r.json().get("results", [])
        reviews = []
        
        for review in results[:10]:  # Limit to 10 reviews
            reviews.append({
                "user_id": review.get("author", "Anonymous"),
                "review_text": review.get("content", ""),
                "rating": None,  # TMDB API reviews don't have ratings
                "created_at": review.get("created_at"),
                "source": "tmdb"
            })
        
        return reviews
    except Exception as e:
        print(f"Error fetching TMDB reviews: {e}")
        return []


def get_google_books_reviews(book_id: str):
    """Fetch reviews/ratings from Google Books API for a specific book."""
    try:
        params = {"key": os.getenv("GOOGLE_BOOKS_API_KEY", "")}
        r = requests.get(f"{GOOGLE_BOOKS_URL}/{book_id}", params=params)
        
        if r.status_code != 200:
            return []
        
        data = r.json()
        volume_info = data.get("volumeInfo", {})
        reviews_list = volume_info.get("reviewsList", [])
        
        reviews = []
        
        # Google Books gives a list of reviews
        if reviews_list:
            for review in reviews_list[:10]:  # Limit to 10 reviews
                reviews.append({
                    "user_id": review.get("author", "Anonymous"),
                    "review_text": review.get("reviewText", review.get("content", "")),
                    "rating": review.get("rating"),
                    "created_at": None,  # Google Books API doesn't provide created_at
                    "source": "google_books"
                })
        
        return reviews
    except Exception as e:
        print(f"Error fetching Google Books reviews: {e}")
        return []