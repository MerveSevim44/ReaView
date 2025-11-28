import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_RrZHU9sTO4Wb@ep-super-glitter-ag00m0lo-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

# Load from env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

inspector = inspect(engine)
tables = inspector.get_table_names()

print("📊 NEON VERİTABANI ŞEMASI:")
print("="*60)

for table in sorted(tables):
    print(f"\n📋 {table}:")
    columns = inspector.get_columns(table)
    for col in columns:
        nullable = "✓ NULL" if col['nullable'] else "✗ NOT NULL"
        print(f"   - {col['name']:<20} {str(col['type']):<20} ({nullable})")
    
    # Show foreign keys
    fks = inspector.get_foreign_keys(table)
    if fks:
        print(f"   🔗 Foreign Keys:")
        for fk in fks:
            print(f"      - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")

print("\n" + "="*60)
print(f"✅ Toplam tablo sayısı: {len(tables)}")
print(f"📋 Tablolar: {', '.join(sorted(tables))}")
