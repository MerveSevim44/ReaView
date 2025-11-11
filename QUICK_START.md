# ⚡ Quick Start: Safe Schema Update for Neon.tech

## TL;DR

Your items table exists. You need to:

1. **Run SQL migration** (won't break anything)
2. **Backend already updated** (no code changes needed)
3. **Test the API**

---

## Step 1: Apply Database Migration

### Copy This SQL

```sql
-- Safe ALTER TABLE commands (Neon.tech compatible)
ALTER TABLE items ADD COLUMN IF NOT EXISTS item_type VARCHAR(10) DEFAULT 'book' NOT NULL;
ALTER TABLE items ADD COLUMN IF NOT EXISTS year INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS poster_url VARCHAR(512);
ALTER TABLE items ADD COLUMN IF NOT EXISTS genres TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS authors TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS page_count INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS director VARCHAR(256);
ALTER TABLE items ADD COLUMN IF NOT EXISTS actors TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS external_api_source VARCHAR(50);
ALTER TABLE items ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Add unique constraint (prevents duplicate movie/book imports)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'items' AND constraint_name = 'uix_item_title_type'
    ) THEN
        ALTER TABLE items ADD CONSTRAINT uix_item_title_type UNIQUE (title, item_type);
    END IF;
END$$;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);
CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type);
CREATE INDEX IF NOT EXISTS idx_items_title_type ON items(title, item_type);
CREATE INDEX IF NOT EXISTS idx_items_year ON items(year);
CREATE INDEX IF NOT EXISTS idx_items_external_source ON items(external_api_source);
```

### Paste Into Neon.tech SQL Editor

1. Go to **Neon.tech Dashboard**
2. Click **SQL Editor**
3. Paste the SQL above
4. Click **Run**
5. ✅ Done!

---

## Step 2: Backend Changes Already Done ✅

Your backend is **already updated**:

- ✅ `models.py` - Item model has all new fields
- ✅ `schemas.py` - ItemOut includes all metadata
- ✅ `services/external_api.py` - Fetches director, actors, genres, authors
- ✅ `routes/external.py` - Imports enriched data to database

**No code changes needed!**

---

## Step 3: Test It

### Restart Backend

```bash
# Press Ctrl+C to stop current server
# Then restart:
cd backend
python -m uvicorn app.main:app --reload
```

### Import a Movie

```bash
curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"
```

**Expected Response:**
```json
{
    "message": "İçerik başarıyla eklendi.",
    "item_id": 42,
    "item": {
        "item_id": 42,
        "title": "Inception",
        "year": 2010,
        "poster_url": "https://image.tmdb.org/...",
        "genres": "Action, Sci-Fi, Thriller",
        "director": "Christopher Nolan",
        "actors": "Leonardo DiCaprio, Marion Cotillard, Ellen Page, Tom Hardy, Joseph Gordon-Levitt",
        "external_api_source": "tmdb",
        ...
    }
}
```

### Import a Book

```bash
curl -X POST "http://localhost:8000/external/import?type=book&query=harry+potter"
```

**Expected Response:**
```json
{
    "message": "İçerik başarıyla eklendi.",
    "item_id": 100,
    "item": {
        "item_id": 100,
        "title": "Harry Potter and the Philosopher's Stone",
        "year": 1997,
        "authors": "J.K. Rowling",
        "page_count": 309,
        "genres": "Fiction, Fantasy, Magic",
        "poster_url": "https://...",
        "external_api_source": "google_books",
        ...
    }
}
```

### Retrieve from DB

```bash
curl "http://localhost:8000/items/42"
```

Should return all fields including new ones!

---

## What Changed

### Database Changes
- 10 new columns added safely
- 1 unique constraint (prevents duplicate movie/book)
- 5 new indexes (faster queries)

### Code Changes
- Models support new fields ✅
- API returns new fields ✅
- External APIs fetch new metadata ✅

### What Stayed the Same
- Existing columns untouched
- Existing data preserved
- Existing API responses backward compatible

---

## Files You Need to Know

| File | Purpose |
|------|---------|
| `backend/migrations/001_extend_items_table.sql` | SQL to run on Neon.tech |
| `backend/app/models.py` | SQLAlchemy Item model (UPDATED) |
| `backend/app/schemas.py` | Pydantic ItemOut schema (UPDATED) |
| `backend/app/services/external_api.py` | API fetching (UPDATED) |
| `backend/app/routes/external.py` | /external/import route (UPDATED) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Migration fails with "column already exists" | Safe - script uses IF NOT EXISTS, won't error |
| API returns old fields only | Restart backend server |
| Duplicate constraint error on insert | Data cleanup needed (see NEON_MIGRATION_GUIDE.md) |
| "Role does not have permissions" | Use Neon.tech SQL Editor instead of CLI |

---

## ✅ Complete Checklist

- [ ] Copy SQL migration script
- [ ] Paste into Neon.tech SQL Editor
- [ ] Run migration
- [ ] Verify columns exist (see guide for SELECT query)
- [ ] Restart FastAPI backend
- [ ] Test: `curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"`
- [ ] Check response includes: director, actors, genres, year, poster_url
- [ ] Test book import: `curl -X POST "http://localhost:8000/external/import?type=book&query=harry+potter"`
- [ ] Check response includes: authors, page_count, genres, year, poster_url

---

## Documentation Files

- **NEON_MIGRATION_GUIDE.md** - Detailed migration instructions + troubleshooting
- **REFACTORING_GUIDE.md** - Complete technical documentation
- **backend/migrations/001_extend_items_table.sql** - SQL migration script

All backend code is ready to go! 🚀
