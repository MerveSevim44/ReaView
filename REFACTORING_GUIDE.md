# ReaView External API Integration Refactoring

## Overview
This document describes the refactoring of the `items` table and backend logic to fully support external API integration as per project requirement **2.2.1 "Data Source: External API Integration"**.

The items table is now the **single source of truth** for all movie and book metadata imported from external APIs (TMDb, Google Books, OpenLibrary).

---

## 1. Database Schema Changes

### Updated Items Table (SQLAlchemy Model)

**File:** `backend/app/models.py`

```python
class Item(Base):
    __tablename__ = "items"

    # Primary Key
    item_id = Column(Integer, primary_key=True, index=True)
    
    # Core Fields (unchanged)
    title = Column(String(256), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # External API Integration Fields
    item_type = Column(String(10), nullable=False, default='book')  # 'movie' or 'book'
    year = Column(Integer, nullable=True)
    poster_url = Column(String(512), nullable=True)
    genres = Column(Text, nullable=True)  # Comma-separated: "Action, Sci-Fi, Thriller"
    
    # Book-specific fields
    authors = Column(Text, nullable=True)  # Comma-separated: "J.K. Rowling, Author Two"
    page_count = Column(Integer, nullable=True)
    
    # Movie-specific fields
    director = Column(String(256), nullable=True)
    actors = Column(Text, nullable=True)  # Comma-separated: "Actor 1, Actor 2, Actor 3"
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    external_api_source = Column(String(50), nullable=True)  # 'tmdb', 'google_books', 'openlibrary'
    
    # Constraints & Indexes
    __table_args__ = (
        UniqueConstraint('title', 'item_type', name='uix_item_title_type'),
        Index('idx_title_type', 'title', 'item_type'),
        Index('idx_item_type', 'item_type'),
        Index('idx_year', 'year'),
    )
```

### Field Descriptions

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `item_type` | VARCHAR(10) | Distinguishes movies from books | 'movie', 'book' |
| `year` | INTEGER | Release/publication year | 2023 |
| `poster_url` | VARCHAR(512) | Cover/poster image URL | 'https://image.tmdb.org/...' |
| `genres` | TEXT | Content categories | 'Action, Sci-Fi, Thriller' |
| `authors` | TEXT | Book authors (comma-separated) | 'J.K. Rowling' |
| `page_count` | INTEGER | Book page count | 309 |
| `director` | VARCHAR(256) | Movie director | 'Christopher Nolan' |
| `actors` | TEXT | Movie cast (top 5, comma-separated) | 'Actor1, Actor2, Actor3' |
| `external_api_source` | VARCHAR(50) | Which API provided the data | 'tmdb', 'google_books', 'openlibrary' |
| `created_at` | TIMESTAMP | Import timestamp | AUTO |
| `updated_at` | TIMESTAMP | Last update timestamp | AUTO |

### Constraints & Indexes

- **Unique Constraint (title, item_type):** Prevents duplicate imports of the same movie/book
  - Example: "Inception" (movie) and "Inception" (book) are different items
  - Same title + same type = DUPLICATE (rejected)

- **Indexes:**
  - `idx_title`: Fast keyword search by title
  - `idx_item_type`: Fast filtering by media type
  - `idx_title_type`: Fast duplicate detection
  - `idx_year`: Fast filtering by year

### PostgreSQL Migration

**File:** `backend/migrations/001_extend_items_table.sql`

Run this SQL after creating the base items table:

```sql
ALTER TABLE items
ADD COLUMN IF NOT EXISTS item_type VARCHAR(10) DEFAULT 'book' NOT NULL,
ADD COLUMN IF NOT EXISTS year INTEGER,
ADD COLUMN IF NOT EXISTS poster_url VARCHAR(512),
ADD COLUMN IF NOT EXISTS genres TEXT,
ADD COLUMN IF NOT EXISTS authors TEXT,
ADD COLUMN IF NOT EXISTS page_count INTEGER,
ADD COLUMN IF NOT EXISTS director VARCHAR(256),
ADD COLUMN IF NOT EXISTS actors TEXT,
ADD COLUMN IF NOT EXISTS external_api_source VARCHAR(50),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

ALTER TABLE items
ADD CONSTRAINT uix_item_title_type UNIQUE (title, item_type);

CREATE INDEX idx_items_title ON items(title);
CREATE INDEX idx_items_type ON items(item_type);
CREATE INDEX idx_items_title_type ON items(title, item_type);
CREATE INDEX idx_items_year ON items(year);
CREATE INDEX idx_items_external_source ON items(external_api_source);
```

---

## 2. Pydantic Schemas (FastAPI)

**File:** `backend/app/schemas.py`

### ItemCreate (Input Schema for API)

```python
class ItemCreate(BaseModel):
    item_type: str = 'book'
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    poster_url: Optional[str] = None
    genres: Optional[str] = None
    authors: Optional[str] = None
    page_count: Optional[int] = None
    director: Optional[str] = None
    actors: Optional[str] = None
    external_api_source: Optional[str] = None
```

### ItemOut (Output Schema for API)

```python
class ItemOut(BaseModel):
    item_id: int
    title: str
    description: Optional[str] = None
    item_type: str
    year: Optional[int] = None
    poster_url: Optional[str] = None
    genres: Optional[str] = None
    authors: Optional[str] = None
    page_count: Optional[int] = None
    director: Optional[str] = None
    actors: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    external_api_source: Optional[str] = None
    
    model_config = {"from_attributes": True}
```

---

## 3. External API Service

**File:** `backend/app/services/external_api.py`

### Data Normalization Pipeline

Each API (TMDb, Google Books, OpenLibrary) returns different formats. The service normalizes all data into a **consistent dictionary format**:

```python
{
    "title": str,
    "description": str,
    "year": int,
    "poster_url": str,
    "item_type": str,  # 'movie' or 'book'
    "external_api_source": str,  # 'tmdb', 'google_books', 'openlibrary'
    "genres": str,  # Comma-separated
    "authors": str,  # For books (comma-separated)
    "page_count": int,  # For books
    "director": str,  # For movies
    "actors": str,  # For movies (comma-separated)
}
```

### search_tmdb(query: str)

**Purpose:** Search The Movie Database API for movies

**Steps:**
1. Call `/search/movie` endpoint
2. For each result, fetch movie details (`/movie/{id}`) to get:
   - Genres
   - Credits (director & top 5 actors)
3. Return normalized list of movie dictionaries

**Example Output:**
```python
[
    {
        "title": "Inception",
        "description": "A thief is given the inverse task of planting an idea...",
        "year": 2010,
        "poster_url": "https://image.tmdb.org/t/p/w500/...",
        "item_type": "movie",
        "external_api_source": "tmdb",
        "genres": "Action, Sci-Fi, Thriller",
        "director": "Christopher Nolan",
        "actors": "Leonardo DiCaprio, Marion Cotillard, Ellen Page, Tom Hardy, Joseph Gordon-Levitt"
    },
    ...
]
```

### search_google_books(query: str)

**Purpose:** Search Google Books API for books

**Steps:**
1. Call `/books/v1/volumes` endpoint
2. Extract from `volumeInfo`:
   - Authors array → join with ", "
   - Categories → join with ", "
   - pageCount
3. Return normalized list of book dictionaries

**Example Output:**
```python
[
    {
        "title": "Harry Potter and the Philosopher's Stone",
        "description": "Harry Potter is a young wizard who...",
        "year": 1997,
        "poster_url": "https://...",
        "item_type": "book",
        "external_api_source": "google_books",
        "authors": "J.K. Rowling",
        "page_count": 309,
        "genres": "Fiction, Fantasy, Magic"
    },
    ...
]
```

### search_openlibrary(query: str)

**Purpose:** Fallback book search using OpenLibrary API

**Steps:**
1. Call `/search.json` endpoint
2. Extract:
   - `author_name` array → join with ", "
   - `subject` array → take top 5, join with ", "
   - `number_of_pages_median`
   - `cover_i` → build cover image URL
3. Return normalized list of book dictionaries

**Example Output:**
```python
[
    {
        "title": "Harry Potter and the Philosopher's Stone",
        "description": "",
        "year": 1997,
        "poster_url": "https://covers.openlibrary.org/b/id/123456-L.jpg",
        "item_type": "book",
        "external_api_source": "openlibrary",
        "authors": "J.K. Rowling",
        "page_count": 309,
        "genres": "Fiction, Fantasy, Wizards"
    },
    ...
]
```

---

## 4. FastAPI Routes

**File:** `backend/app/routes/external.py`

### Endpoint: `/external/search`

**Purpose:** Search external APIs without saving to database

**Method:** GET

**Parameters:**
- `type` (required): `movie` or `book`
- `query` (required): Search term (min 2 characters)

**Example Requests:**
```
GET /external/search?type=movie&query=inception
GET /external/search?type=book&query=harry+potter
```

**Response:** JSON array of results (see data normalization format above)

**Status Code:** 200 OK or 500 (API error)

### Endpoint: `/external/import`

**Purpose:** Search external APIs and save matching items to database

**Method:** POST

**Parameters:**
- `type` (required): `movie` or `book`
- `query` (required): Search term (min 2 characters)

**Example Requests:**
```
POST /external/import?type=movie&query=inception
POST /external/import?type=book&query=harry+potter
```

**Logic Flow:**
1. Call appropriate search function (`search_tmdb` or `search_google_books` → fallback to `search_openlibrary`)
2. Take the first result
3. Check if item exists using unique constraint `(title, item_type)`
   - If exists: Return 200 with existing item ID (no duplicate created)
   - If not exists: Insert into database
4. Return success message with inserted item

**Success Response (200 OK):**
```json
{
    "message": "İçerik başarıyla eklendi.",
    "item": {
        "item_id": 42,
        "title": "Inception",
        "description": "A thief is given the inverse task...",
        "item_type": "movie",
        "year": 2010,
        "poster_url": "https://image.tmdb.org/...",
        "genres": "Action, Sci-Fi, Thriller",
        "director": "Christopher Nolan",
        "actors": "Leonardo DiCaprio, Marion Cotillard, Ellen Page, Tom Hardy, Joseph Gordon-Levitt",
        "external_api_source": "tmdb",
        "created_at": "2024-11-11T10:30:00Z",
        "updated_at": "2024-11-11T10:30:00Z"
    },
    "item_id": 42
}
```

**Duplicate Response (200 OK):**
```json
{
    "message": "Bu içerik zaten veritabanında mevcut.",
    "item_id": 42,
    "item": {...}
}
```

**Not Found Response (200 OK):**
```json
{
    "message": "Hiç veri bulunamadı."
}
```

**Error Response (500):**
```json
{
    "detail": "Veritabanı hatası: ..."
}
```

---

## 5. Related Endpoints (Updated)

### GET /items

**Purpose:** List all items from database

**Returns:** All fields including new metadata fields

```json
[
    {
        "item_id": 1,
        "title": "Inception",
        "description": "A thief is given the inverse task...",
        "item_type": "movie",
        "year": 2010,
        "poster_url": "https://...",
        "genres": "Action, Sci-Fi, Thriller",
        "director": "Christopher Nolan",
        "actors": "Leonardo DiCaprio, ...",
        "external_api_source": "tmdb",
        "created_at": "2024-11-11T10:30:00Z",
        "updated_at": "2024-11-11T10:30:00Z"
    },
    ...
]
```

### GET /items/{item_id}

**Purpose:** Get single item by ID

**Returns:** All metadata fields (see above)

---

## 6. Usage Examples

### Example 1: Import a Movie

```bash
# 1. Search and import
curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"

# Response:
# {
#     "message": "İçerik başarıyla eklendi.",
#     "item_id": 42,
#     "item": {
#         "item_id": 42,
#         "title": "Inception",
#         "year": 2010,
#         "director": "Christopher Nolan",
#         "actors": "Leonardo DiCaprio, Marion Cotillard, ...",
#         ...
#     }
# }

# 2. Retrieve from database
curl "http://localhost:8000/items/42"

# Response includes all metadata from the movie import
```

### Example 2: Import a Book

```bash
# 1. Search and import
curl -X POST "http://localhost:8000/external/import?type=book&query=harry+potter"

# Response:
# {
#     "message": "İçerik başarıyla eklendi.",
#     "item_id": 100,
#     "item": {
#         "item_id": 100,
#         "title": "Harry Potter and the Philosopher's Stone",
#         "year": 1997,
#         "authors": "J.K. Rowling",
#         "page_count": 309,
#         "genres": "Fiction, Fantasy, Magic",
#         ...
#     }
# }

# 2. Retrieve from database
curl "http://localhost:8000/items/100"
```

### Example 3: Prevent Duplicates

```bash
# First import
curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"
# Returns item_id: 42

# Second import (same query)
curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"
# Returns existing item_id: 42 (no duplicate created)
```

---

## 7. Data Flow Diagram

```
User/Frontend
    |
    v
POST /external/import?type=movie&query=inception
    |
    v
Backend: external.py (import_item route)
    |
    v
Search External API (search_tmdb)
    |
    v
Normalize Data (external_api.py)
    |
    v
Check Unique Constraint (title, item_type)
    |
    +---> Exists: Return existing item ID
    |
    +---> Not exists: Insert to database
                        |
                        v
                   PostgreSQL items table
                        |
                        v
                   Return ItemOut schema
```

---

## 8. Implementation Checklist

- [x] Update SQLAlchemy Item model with all fields
- [x] Add unique constraint `(title, item_type)`
- [x] Add database indexes for performance
- [x] Update Pydantic schemas (ItemCreate, ItemOut)
- [x] Enhance `search_tmdb()` to fetch director/actors/genres
- [x] Enhance `search_google_books()` to fetch authors/page_count/genres
- [x] Enhance `search_openlibrary()` to fetch authors/page_count/genres
- [x] Update `/external/import` route logic
- [x] Add IntegrityError handling for duplicate detection
- [x] Create PostgreSQL migration script
- [x] Document all changes

---

## 9. PEP8 Compliance

All code follows Python best practices:
- Type hints on all functions
- Docstrings for module/function-level documentation
- 4-space indentation
- Meaningful variable names
- Comments for complex logic
- Proper error handling with try/except

---

## 10. Testing Recommendations

1. **Unit Tests:**
   - Test each `search_*()` function independently
   - Mock API responses
   - Verify data normalization

2. **Integration Tests:**
   - Test `/external/import` with real APIs
   - Verify duplicate detection
   - Verify database insertion

3. **Manual Testing:**
   - Import movies: `curl -X POST "http://localhost:8000/external/import?type=movie&query=MOVIE_NAME"`
   - Import books: `curl -X POST "http://localhost:8000/external/import?type=book&query=BOOK_NAME"`
   - Verify database via: `SELECT * FROM items;`

---

## 11. Future Enhancements

1. **Batch Import:** `/external/import/batch` to import multiple items
2. **Search within DB:** `/items/search?query=...` for keyword search
3. **Update Endpoint:** Re-fetch metadata from APIs to update stale items
4. **Rating System:** Add `rating` field once user ratings are implemented
5. **Review Count:** Cache review counts in items table for faster queries
6. **Caching:** Cache API responses to reduce external API calls

---

## Conclusion

This refactoring fully implements requirement **2.2.1 "Data Source: External API Integration"**. The `items` table is now the **single source of truth** for all external data, with proper constraints, indexes, and normalized schemas across all APIs.
