# ✅ Complete Checklist: ReaView External API Integration

## Pre-Migration Checklist

### ✅ Code Review
- [x] Models updated with new fields
- [x] Schemas updated with new fields
- [x] External API service enhanced
- [x] Routes logic updated
- [x] Error handling implemented
- [x] Type hints added throughout
- [x] Code follows PEP8

### ✅ Documentation
- [x] QUICK_START.md created
- [x] NEON_MIGRATION_GUIDE.md created
- [x] REFACTORING_GUIDE.md created
- [x] IMPLEMENTATION_SUMMARY.md created
- [x] VISUAL_GUIDE.md created
- [x] SQL migration script created

### ✅ Backup
- [ ] Backup Neon.tech database (recommended)
  ```sql
  -- Run on Neon.tech before migration
  pg_dump -h pg-xxxxx.neon.tech -U your_user -d neon > backup.sql
  ```
- [ ] Backup application code (if using git)
  ```bash
  git commit -m "Pre-migration backup"
  ```

---

## Migration Execution Checklist

### Step 1: Database Migration

**File:** `backend/migrations/001_extend_items_table.sql`

- [ ] Open Neon.tech Dashboard
- [ ] Click SQL Editor
- [ ] Copy migration SQL
  ```sql
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
  
  DO $$
  BEGIN
      IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                     WHERE table_name = 'items' AND constraint_name = 'uix_item_title_type') THEN
          ALTER TABLE items ADD CONSTRAINT uix_item_title_type UNIQUE (title, item_type);
      END IF;
  END$$;
  
  CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);
  CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type);
  CREATE INDEX IF NOT EXISTS idx_items_title_type ON items(title, item_type);
  CREATE INDEX IF NOT EXISTS idx_items_year ON items(year);
  CREATE INDEX IF NOT EXISTS idx_items_external_source ON items(external_api_source);
  ```
- [ ] Click Run
- [ ] Verify no errors
- [ ] Check command completed successfully

### Step 2: Verify Database Changes

- [ ] Run verification query:
  ```sql
  SELECT column_name, data_type, is_nullable 
  FROM information_schema.columns 
  WHERE table_name = 'items' 
  ORDER BY ordinal_position;
  ```
- [ ] Verify all 10 new columns exist:
  - [ ] item_type
  - [ ] year
  - [ ] poster_url
  - [ ] genres
  - [ ] authors
  - [ ] page_count
  - [ ] director
  - [ ] actors
  - [ ] external_api_source
  - [ ] updated_at

- [ ] Verify constraint exists:
  ```sql
  SELECT constraint_name FROM information_schema.table_constraints 
  WHERE table_name = 'items' AND constraint_name = 'uix_item_title_type';
  ```

- [ ] Verify indexes exist:
  ```sql
  SELECT indexname FROM pg_indexes WHERE tablename = 'items';
  ```
  Should show:
  - [ ] idx_items_title
  - [ ] idx_items_type
  - [ ] idx_items_title_type
  - [ ] idx_items_year
  - [ ] idx_items_external_source

### Step 3: Backend Server Setup

- [ ] Verify `models.py` has new fields:
  ```bash
  grep -c "item_type\|year\|poster_url\|genres\|authors\|page_count\|director\|actors\|external_api_source\|updated_at" backend/app/models.py
  ```
  Should return: 10+ matches

- [ ] Verify `schemas.py` has new fields in ItemOut
- [ ] Verify `external_api.py` has enhanced functions
- [ ] Verify `routes/external.py` has updated logic

- [ ] Restart FastAPI server:
  ```bash
  # Stop current server (Ctrl+C)
  # Restart
  cd backend
  python -m uvicorn app.main:app --reload
  ```

- [ ] Check for startup errors:
  ```
  INFO:     Uvicorn running on http://127.0.0.1:8000
  INFO:     Application startup complete
  ```

---

## Testing Checklist

### Test 1: Movie Import

```bash
curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"
```

Expected Response: ✅ 200 OK
```json
{
    "message": "İçerik başarıyla eklendi.",
    "item_id": <number>,
    "item": {
        "item_id": <number>,
        "title": "Inception",
        "item_type": "movie",
        "year": 2010,
        "poster_url": "https://...",
        "genres": "Action, Sci-Fi, Thriller",
        "director": "Christopher Nolan",
        "actors": "Leonardo DiCaprio, Marion Cotillard, ...",
        "external_api_source": "tmdb"
    }
}
```

- [ ] Response status is 200 OK
- [ ] Message contains "успешно" (successfully)
- [ ] item_id is an integer
- [ ] title is correct
- [ ] item_type is "movie"
- [ ] year is 2010
- [ ] director is present and not null
- [ ] actors is present and not null
- [ ] genres is present and not null
- [ ] external_api_source is "tmdb"

### Test 2: Book Import

```bash
curl -X POST "http://localhost:8000/external/import?type=book&query=harry+potter"
```

Expected Response: ✅ 200 OK
```json
{
    "message": "İçerik başarıyla eklendi.",
    "item_id": <number>,
    "item": {
        "item_id": <number>,
        "title": "Harry Potter and the Philosopher's Stone",
        "item_type": "book",
        "year": 1997,
        "authors": "J.K. Rowling",
        "page_count": 309,
        "genres": "Fiction, Fantasy, Magic",
        "poster_url": "https://...",
        "external_api_source": "google_books"
    }
}
```

- [ ] Response status is 200 OK
- [ ] item_type is "book"
- [ ] authors is present and not null
- [ ] page_count is present and is an integer
- [ ] genres is present and not null
- [ ] year is 1997
- [ ] external_api_source is "google_books" or "openlibrary"

### Test 3: Duplicate Prevention

```bash
# Import same movie twice
curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"
curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"
```

Expected: ✅ Second request returns same item_id
```json
{
    "message": "Bu içerik zaten veritabanında mevcut.",
    "item_id": <same number as first>,
    "item": {...}
}
```

- [ ] Both requests have same item_id
- [ ] Second response says item already exists
- [ ] No duplicate created in database

### Test 4: Retrieve from Database

```bash
# Replace 42 with actual item_id from previous tests
curl "http://localhost:8000/items/42"
```

Expected Response: ✅ 200 OK with all fields

- [ ] Response includes all original fields
- [ ] Response includes all 10 new fields
- [ ] No fields are null (except optionally director for books, authors for movies)

### Test 5: List All Items

```bash
curl "http://localhost:8000/items"
```

Expected Response: ✅ 200 OK with array of items

- [ ] Returns array (not empty)
- [ ] Each item includes new fields
- [ ] item_type values are either "movie" or "book"

### Test 6: Database Verification

```sql
-- Check items table
SELECT item_id, title, item_type, year, director, authors, page_count 
FROM items 
ORDER BY item_id DESC 
LIMIT 5;
```

Expected: ✅ Shows recent imports with data

- [ ] Movies have director, actors, genres filled
- [ ] Books have authors, page_count, genres filled
- [ ] item_type is correct ("movie" or "book")
- [ ] Data matches API response

---

## Performance Testing Checklist

### Index Performance

- [ ] Query with title (should use index):
  ```sql
  EXPLAIN ANALYZE SELECT * FROM items WHERE title LIKE '%Inception%';
  ```
  Look for "Index Scan" not "Seq Scan"

- [ ] Query with type (should use index):
  ```sql
  EXPLAIN ANALYZE SELECT * FROM items WHERE item_type = 'movie';
  ```
  Look for "Index Scan"

- [ ] Query with title + type (should use composite index):
  ```sql
  EXPLAIN ANALYZE SELECT * FROM items WHERE title = 'Inception' AND item_type = 'movie';
  ```
  Look for "Index Scan on idx_items_title_type"

### Response Time

- [ ] Import request completes in < 2 seconds (not counting API call)
- [ ] Duplicate check is instant
- [ ] List items (/items) returns < 100ms for 1000 items
- [ ] Retrieve single item (/items/42) returns < 50ms

---

## Error Handling Checklist

### Test Invalid Requests

- [ ] Test with invalid type:
  ```bash
  curl -X POST "http://localhost:8000/external/import?type=invalid&query=test"
  ```
  Expected: ❌ 422 Validation Error

- [ ] Test with query too short:
  ```bash
  curl -X POST "http://localhost:8000/external/import?type=movie&query=a"
  ```
  Expected: ❌ 422 Validation Error

- [ ] Test with non-existent API item:
  ```bash
  curl -X POST "http://localhost:8000/external/import?type=movie&query=xyzabc123notarealfilm"
  ```
  Expected: ✅ 200 with "Hiç veri bulunamadı."

- [ ] Test without parameters:
  ```bash
  curl -X POST "http://localhost:8000/external/import"
  ```
  Expected: ❌ 422 Missing required parameters

### Test Database Errors

- [ ] Monitor backend logs for IntegrityError
- [ ] Monitor for connection errors
- [ ] Check for any unhandled exceptions

---

## Post-Migration Checklist

### Data Integrity

- [ ] No data loss from existing items
- [ ] All existing reviews still work
- [ ] All existing activities still work
- [ ] Foreign key constraints still valid

### Backup & Documentation

- [ ] Code committed to git with clear message
  ```bash
  git commit -m "Refactor: Add external API metadata to items table"
  ```
- [ ] Migration script saved in version control
- [ ] Documentation committed alongside code
- [ ] Team notified of changes

### Monitoring

- [ ] Set up alerts for database errors
- [ ] Monitor API error rate
- [ ] Check for slow queries
- [ ] Monitor disk space usage

---

## Frontend Updates Checklist (Optional)

If updating frontend to show new fields:

- [ ] Update item detail page to show:
  - [ ] director (movies)
  - [ ] actors (movies)
  - [ ] authors (books)
  - [ ] page_count (books)
  - [ ] genres (both)
  - [ ] year (both)

- [ ] Update item cards to display:
  - [ ] poster_url (already has this)
  - [ ] item_type badge
  - [ ] genres list

- [ ] Add filters for:
  - [ ] item_type (Movies vs Books)
  - [ ] genres
  - [ ] year range

---

## Rollback Plan (If Needed)

If something goes wrong:

```sql
-- Remove new columns (CAREFUL - will delete data)
ALTER TABLE items DROP COLUMN IF EXISTS item_type CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS year CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS poster_url CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS genres CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS authors CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS page_count CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS director CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS actors CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS external_api_source CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS updated_at CASCADE;

-- Remove constraint
ALTER TABLE items DROP CONSTRAINT IF EXISTS uix_item_title_type;

-- Remove indexes
DROP INDEX IF EXISTS idx_items_title;
DROP INDEX IF EXISTS idx_items_type;
DROP INDEX IF EXISTS idx_items_title_type;
DROP INDEX IF EXISTS idx_items_year;
DROP INDEX IF EXISTS idx_items_external_source;
```

⚠️ **Only use rollback if absolutely necessary - will delete new data!**

- [ ] Restore from backup if rollback needed:
  ```bash
  psql -h pg-xxxxx.neon.tech -U your_user -d neon < backup.sql
  ```

---

## Sign-Off

**Migration Date:** ________________  
**Executed By:** ________________  
**Verified By:** ________________  

### Final Status

- [ ] All tests passed ✅
- [ ] No production issues reported
- [ ] Documentation complete
- [ ] Team trained
- [ ] Ready for production ✅

---

**Version:** 1.0  
**Last Updated:** November 11, 2025  
**Status:** Ready for Deployment
