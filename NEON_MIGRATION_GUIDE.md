# Safe PostgreSQL Migration for Neon.tech

## How to Apply the Migration

### Option 1: Using Neon.tech Console SQL Editor (Recommended)

1. Go to your Neon.tech dashboard
2. Click **SQL Editor**
3. Copy the contents of `backend/migrations/001_extend_items_table.sql`
4. Paste into the SQL editor
5. Click **Run**
6. ✅ Done!

### Option 2: Using psql Command Line

```bash
psql -h pg-xxxxx.neon.tech -U your_username -d neon -f backend/migrations/001_extend_items_table.sql
```

Replace:
- `pg-xxxxx.neon.tech` with your Neon.tech host
- `your_username` with your database user
- `neon` with your database name

### Option 3: Using Python (if needed)

```python
import psycopg2

conn = psycopg2.connect(
    host="pg-xxxxx.neon.tech",
    user="your_user",
    password="your_password",
    database="neon"
)

cursor = conn.cursor()

# Read migration file
with open('backend/migrations/001_extend_items_table.sql', 'r') as f:
    sql = f.read()

# Execute
cursor.execute(sql)
conn.commit()
cursor.close()
conn.close()

print("✅ Migration applied successfully!")
```

---

## What Gets Added

### New Columns (All Safe - Won't Error If Already Exist)

| Column | Type | Purpose | Example |
|--------|------|---------|---------|
| `item_type` | VARCHAR(10) | 'movie' or 'book' | movie |
| `year` | INTEGER | Release/publication year | 2023 |
| `poster_url` | VARCHAR(512) | Cover image URL | https://... |
| `genres` | TEXT | Comma-separated genres | Action, Sci-Fi, Thriller |
| `authors` | TEXT | Book authors | J.K. Rowling |
| `page_count` | INTEGER | Book pages | 309 |
| `director` | VARCHAR(256) | Movie director | Christopher Nolan |
| `actors` | TEXT | Comma-separated cast | Actor1, Actor2, Actor3 |
| `external_api_source` | VARCHAR(50) | API source | tmdb, google_books, openlibrary |
| `updated_at` | TIMESTAMP | Last update timestamp | AUTO |

### New Constraint

- **Unique Constraint:** `(title, item_type)` - Prevents duplicate imports
  - Same title + same type = REJECTED
  - "Inception" (movie) + "Inception" (book) = ALLOWED

### New Indexes

- `idx_items_title` - Search by title
- `idx_items_type` - Filter by type
- `idx_items_title_type` - Duplicate detection
- `idx_items_year` - Filter by year
- `idx_items_external_source` - Filter by API source

---

## Verification After Migration

Run this query to verify all columns were added:

```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'items' 
ORDER BY ordinal_position;
```

Expected columns (should include all new ones):
```
item_id                  | integer
title                    | character varying
description              | text
item_type                | character varying      ← NEW
year                     | integer                ← NEW
poster_url               | character varying      ← NEW
genres                   | text                   ← NEW
authors                  | text                   ← NEW
page_count               | integer                ← NEW
director                 | character varying      ← NEW
actors                   | text                   ← NEW
external_api_source      | character varying      ← NEW
updated_at               | timestamp with time zone ← NEW
created_at               | timestamp with time zone (existing)
```

---

## Troubleshooting

### Error: "Column already exists"
**Solution:** This won't happen because we use `IF NOT EXISTS`. The script is safe to run multiple times.

### Error: "Duplicate key violates unique constraint"
**Cause:** Existing rows have duplicate (title, item_type) values
**Solution:** Before running the migration, clean up duplicates:

```sql
-- Keep only the first (oldest) item for each title+type combination
DELETE FROM items a
WHERE a.item_id NOT IN (
    SELECT MIN(item_id)
    FROM items
    GROUP BY title, item_type
);

-- Then run the migration script
```

### Error: "Role does not have permissions"
**Solution:** Use the Neon.tech SQL Editor or ensure your user has ALTER TABLE privileges

---

## Next Steps

After running the migration:

1. **Verify** the columns exist (run the SELECT query above)
2. **Restart** your FastAPI backend server
3. **Test** the import endpoint:
   ```bash
   curl -X POST "http://localhost:8000/external/import?type=movie&query=inception"
   ```
4. **Check** that new fields are populated in the response

---

## Rollback (If Needed)

If something goes wrong, you can remove the new columns:

```sql
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
```

⚠️ **Warning:** This will delete all data in these columns. Only use if absolutely necessary.
