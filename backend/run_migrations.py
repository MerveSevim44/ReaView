#!/usr/bin/env python3
"""
Database Migration Runner
Tüm migration SQL dosyalarını sırayla çalıştırır.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


# Project root'u bul
project_root = Path(__file__).parent.parent
backend_dir = project_root / "backend"
app_dir = backend_dir / "app"
migrations_dir = backend_dir / "migrations"

# .env dosyasını yükle
env_file = app_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

# Database URL'sini al
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # SQLite fallback
    DATABASE_URL = f"sqlite:///{backend_dir / 'dev.db'}"
    print(f"WARNING: DATABASE_URL not set. Using SQLite: {DATABASE_URL}")

print(f"INFO: Database URL: {DATABASE_URL}")

# Engine oluştur
try:
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    print("SUCCESS: Database connection successful")
except Exception as e:
    print(f"ERROR: Database connection failed: {e}")
    sys.exit(1)

# Migration dosyalarını bul
migration_files = sorted(migrations_dir.glob("*.sql"))

if not migration_files:
    print(f"WARNING: No migration files found in {migrations_dir}")
    sys.exit(0)

print(f"\nFound {len(migration_files)} migration files:")
for f in migration_files:
    print(f"   - {f.name}")

# Her migration dosyasını çalıştır
print("\nRunning migrations...\n")
results = []
failed = False

for migration_file in migration_files:
    print(f"Running {migration_file.name}...", end=" ")
    
    try:
        with open(migration_file, "r") as f:
            sql_content = f.read()
        
        # Execute SQL statements
        # Split by semicolon to handle multiple statements
        statements = [s.strip() for s in sql_content.split(";") if s.strip()]
        
        for statement in statements:
            db.execute(text(statement))
        
        db.commit()
        print("SUCCESS")
        results.append((migration_file.name, "SUCCESS"))
        
    except Exception as e:
        error_msg = str(e)
        # Some "errors" are OK (like column already exists)
        if "already exists" in error_msg or "duplicate column" in error_msg:
            print(f"WARNING - Column might already exist (OK)")
            results.append((migration_file.name, "WARNING - Column already exists"))
        else:
            print(f"ERROR: {error_msg}")
            results.append((migration_file.name, f"ERROR: {error_msg[:50]}"))
            failed = True
        db.rollback()

# Sonuç özeti
print("\n" + "="*60)
print("MIGRATION RESULTS SUMMARY")
print("="*60)

for filename, status in results:
    print(f"{filename:40} {status}")

print("="*60)

if failed:
    print("\nWARNING: Some migrations failed. Check the errors above.")
    sys.exit(1)
else:
    print("\nSUCCESS: All migrations completed successfully!")
    sys.exit(0)

db.close()
