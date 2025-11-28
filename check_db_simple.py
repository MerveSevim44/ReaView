import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_RrZHU9sTO4Wb@ep-super-glitter-ag00m0lo-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Query tables
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' 
        ORDER BY table_name
    """))
    
    print("NEON DATABASE TABLES:")
    print("="*60)
    tables = [row[0] for row in result]
    for table in tables:
        print(f"  - {table}")
    
    print(f"\nTotal: {len(tables)} tables")
    
    print("\n" + "="*60)
    print("ACTIVITIES TABLE STRUCTURE:")
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name='activities'
        ORDER BY ordinal_position
    """))
    
    for row in result:
        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
        print(f"  - {row[0]:<20} {row[1]:<20} {nullable}")

print("\nOPERA TION SUCCESS!")
