# 🎯 Visual Guide: External API Integration Setup

## Before vs After

### BEFORE Migration
```
items table
├── item_id
├── title
├── description
└── created_at

❌ No movie/book distinction
❌ No metadata from APIs
❌ No duplicate prevention
```

### AFTER Migration
```
items table
├── item_id
├── title
├── description
├── item_type          ← NEW: 'movie' or 'book'
├── year               ← NEW: Release/publication year
├── poster_url         ← NEW: Cover image
├── genres             ← NEW: Comma-separated
├── authors            ← NEW: For books
├── page_count         ← NEW: For books
├── director           ← NEW: For movies
├── actors             ← NEW: For movies
├── external_api_source ← NEW: API source tracking
├── created_at
└── updated_at         ← NEW: Update tracking

✅ Movie/book distinction
✅ Rich metadata from APIs
✅ Unique constraint prevents duplicates
✅ Performance indexes
```

---

## Data Flow Diagram

```
┌─────────────┐
│   Frontend  │
│   (User)    │
└──────┬──────┘
       │
       │ POST /external/import?type=movie&query=inception
       │
       ▼
┌──────────────────────┐
│   FastAPI Backend    │
│  (external.py)       │
└──────┬───────────────┘
       │
       │ 1. Call API
       │
       ▼
┌────────────────────────────────────┐
│  External API Service              │
│  ├─ search_tmdb()                  │
│  ├─ search_google_books()          │
│  └─ search_openlibrary()           │
│                                    │
│  Returns normalized data:          │
│  {                                 │
│    "title": "Inception",           │
│    "year": 2010,                   │
│    "director": "Nolan",            │
│    "actors": "DiCaprio, ...",      │
│    "genres": "Action, Sci-Fi",     │
│    ...                             │
│  }                                 │
└──────┬─────────────────────────────┘
       │
       │ 2. Check for duplicate
       │
       ▼
┌────────────────────────────────┐
│  Unique Constraint Check       │
│  SELECT * FROM items           │
│  WHERE title = 'Inception'     │
│  AND item_type = 'movie'       │
│                                │
│  ├─ Exists: Return item_id     │
│  └─ New: Insert to DB          │
└──────┬─────────────────────────┘
       │
       │ 3. Save to DB
       │
       ▼
┌────────────────────────────────┐
│  PostgreSQL (Neon.tech)        │
│  items table                   │
│                                │
│  item_id  │ title     │ type   │
│  ─────────┼───────────┼────────│
│  42       │ Inception │ movie  │
│  100      │ Harry ... │ book   │
└──────┬────────────────────────┘
       │
       │ 4. Return response
       │
       ▼
┌──────────────────────┐
│   Frontend / Client  │
│   ItemOut JSON       │
│   (all fields)       │
└──────────────────────┘
```

---

## API Endpoint Map

```
┌─────────────────────────────────────────────┐
│         External API Integration             │
└─────────────────────────────────────────────┘

GET /external/search
├─ Purpose: Search without saving
├─ Parameters: type (movie|book), query
└─ Response: Array of results

POST /external/import
├─ Purpose: Search and save to database
├─ Parameters: type (movie|book), query
├─ Logic:
│  1. Fetch from API
│  2. Check duplicate (title + type)
│  3. Insert if new
│  4. Return ItemOut
└─ Response: Saved item or existing item_id

GET /items
├─ Purpose: List all items
└─ Response: Array of all ItemOut (includes new fields)

GET /items/{item_id}
├─ Purpose: Get single item
└─ Response: ItemOut (includes new fields)
```

---

## Migration Steps Flowchart

```
START
  │
  ├─→ [ ] Prepare SQL migration script
  │        (backend/migrations/001_extend_items_table.sql)
  │
  ├─→ [ ] Open Neon.tech SQL Editor
  │
  ├─→ [ ] Paste SQL & Run
  │
  ├─→ [ ] Verify columns exist
  │        SELECT * FROM information_schema.columns
  │        WHERE table_name = 'items';
  │
  ├─→ [ ] Restart FastAPI backend
  │        python -m uvicorn app.main:app --reload
  │
  ├─→ [ ] Test movie import
  │        curl -X POST "...external/import?type=movie&query=inception"
  │
  ├─→ [ ] Test book import
  │        curl -X POST "...external/import?type=book&query=harry+potter"
  │
  ├─→ [ ] Verify response includes new fields
  │        (director, actors, genres, authors, page_count, etc.)
  │
  └─→ ✅ SUCCESS
        Items table now supports rich metadata!
```

---

## Entity Relationship Diagram

```
┌─────────────────────────────────┐
│          Items Table            │
├─────────────────────────────────┤
│ PK  item_id (INT)              │
│     title (VARCHAR)     ────────┼─ UNIQUE Constraint
│     description (TEXT)          │  with item_type
│     item_type (VARCHAR)  ───────┼─┘
│     year (INT)                  │
│     poster_url (VARCHAR)        │
│     genres (TEXT)               │
│     authors (TEXT)              │
│     page_count (INT)            │
│     director (VARCHAR)          │
│     actors (TEXT)               │
│     external_api_source (VARCHAR)
│     created_at (TIMESTAMP)      │
│     updated_at (TIMESTAMP)      │
│                                 │
│ FK  Indexes:                    │
│ ├─ idx_items_title              │
│ ├─ idx_items_type               │
│ ├─ idx_items_title_type         │
│ ├─ idx_items_year               │
│ └─ idx_items_external_source    │
└─────────────────────────────────┘
           │
           │ Foreign Key References
           │
      ┌────┴─────┐
      │           │
   Reviews    Activities
```

---

## Metadata by Type

### For Movies 🎬
```
{
    "title": "Inception",
    "item_type": "movie",
    ── MOVIE-SPECIFIC FIELDS ──
    "director": "Christopher Nolan",
    "actors": "Leonardo DiCaprio, Marion Cotillard, Ellen Page, Tom Hardy, Joseph Gordon-Levitt",
    "genres": "Action, Sci-Fi, Thriller",
    "year": 2010,
    "poster_url": "https://image.tmdb.org/...",
    "external_api_source": "tmdb",
    ── COMMON FIELDS ──
    "description": "A thief is given the inverse task..."
}
```

### For Books 📖
```
{
    "title": "Harry Potter and the Philosopher's Stone",
    "item_type": "book",
    ── BOOK-SPECIFIC FIELDS ──
    "authors": "J.K. Rowling",
    "page_count": 309,
    "genres": "Fiction, Fantasy, Magic",
    "year": 1997,
    "poster_url": "https://...",
    "external_api_source": "google_books",
    ── COMMON FIELDS ──
    "description": "Harry Potter is a young wizard who..."
}
```

---

## API Response Example

### Movie Import Response
```
HTTP 200 OK
{
    "message": "İçerik başarıyla eklendi.",
    "item_id": 42,
    "item": {
        ├─ IDENTIFIERS
        │  ├─ item_id: 42
        │  ├─ title: "Inception"
        │  └─ item_type: "movie"
        │
        ├─ MOVIE METADATA
        │  ├─ director: "Christopher Nolan"
        │  ├─ actors: "Leonardo DiCaprio, Marion Cotillard, ..."
        │  ├─ genres: "Action, Sci-Fi, Thriller"
        │  └─ year: 2010
        │
        ├─ COMMON METADATA
        │  ├─ description: "A thief is given the inverse..."
        │  ├─ poster_url: "https://image.tmdb.org/..."
        │  └─ external_api_source: "tmdb"
        │
        └─ TIMESTAMPS
           ├─ created_at: "2024-11-11T10:30:00Z"
           └─ updated_at: "2024-11-11T10:30:00Z"
    }
}
```

---

## Database Indexes Impact

### Performance Improvement

```
WITHOUT Indexes:
SELECT * FROM items WHERE title = 'Inception'
└─ Full table scan: O(n) slow

WITH idx_items_title:
SELECT * FROM items WHERE title = 'Inception'
└─ Index lookup: O(log n) FAST ✅

WITHOUT Indexes:
SELECT * FROM items WHERE item_type = 'movie'
└─ Full table scan: O(n) slow

WITH idx_items_type:
SELECT * FROM items WHERE item_type = 'movie'
└─ Index lookup: O(log n) FAST ✅

WITHOUT Indexes (Duplicate Check):
INSERT INTO items (title, item_type, ...)
└─ Full scan to check unique: slow

WITH idx_items_title_type:
INSERT INTO items (title, item_type, ...)
└─ Index lookup: O(log n) FAST ✅
```

---

## File Organization

```
ReaView/
├── backend/
│   └── app/
│       ├── models.py              ✅ UPDATED
│       ├── schemas.py             ✅ UPDATED
│       ├── routes/
│       │   └── external.py        ✅ UPDATED
│       └── services/
│           └── external_api.py    ✅ UPDATED
│
├── migrations/
│   └── 001_extend_items_table.sql ✨ NEW
│
├── QUICK_START.md                 ✨ NEW
├── NEON_MIGRATION_GUIDE.md        ✨ NEW
├── REFACTORING_GUIDE.md           ✨ NEW
└── IMPLEMENTATION_SUMMARY.md      ✨ NEW
```

---

## Timeline to Production

```
Time  │ Action                           │ Status
──────┼──────────────────────────────────┼────────
 0 min│ 1. Copy SQL migration script     │ ⏱️
      │ 2. Open Neon.tech SQL Editor    │
      │ 3. Paste & Run SQL              │
 5 min├──────────────────────────────────┤ ✅
      │ 4. Verify columns exist         │ ⏱️
      │ 5. Restart backend server       │
      │ 6. Test movie import            │
10 min├──────────────────────────────────┤ ✅
      │ 7. Test book import             │
      │ 8. Monitor for errors           │
      │ 9. Update frontend (optional)   │
15 min└──────────────────────────────────┴────────
        🚀 LIVE AND READY
```

---

## Success Criteria

✅ **All Should Be True:**
- [ ] Migration script runs without errors
- [ ] 10 new columns exist in items table
- [ ] Unique constraint `(title, item_type)` created
- [ ] 5 new indexes created
- [ ] Backend starts without errors
- [ ] GET /items returns new fields
- [ ] POST /external/import returns new fields
- [ ] Duplicate prevention works
- [ ] Movie metadata includes: director, actors, genres
- [ ] Book metadata includes: authors, page_count, genres

**If all above are ✅ → Production Ready!**

---

## Quick Reference

| Acronym | Meaning |
|---------|---------|
| PK | Primary Key |
| FK | Foreign Key |
| TMDB | The Movie Database (API) |
| ORM | Object-Relational Mapping |
| CRUD | Create, Read, Update, Delete |

---

**Diagram Version:** 1.0  
**Last Updated:** November 11, 2025  
**Status:** Ready for Production ✅
