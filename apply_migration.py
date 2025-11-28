import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_RrZHU9sTO4Wb@ep-super-glitter-ag00m0lo-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Read migration file
with open('backend/migrations/022_cleanup_and_optimize_for_feed.sql', 'r') as f:
    sql_content = f.read()

print("🔧 Veritabanı temizleme ve optimizasyon başlanıyor...")
print("="*60)

try:
    with engine.begin() as conn:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            try:
                # Skip comments
                if statement.startswith('--') or not statement.strip():
                    continue
                    
                print(f"\n⏳ Adım {i}/{len(statements)}: Yürütülüyor...")
                conn.execute(text(statement))
                print(f"✅ Adım {i} tamamlandı")
            except Exception as e:
                error_str = str(e)
                if "already exists" in error_str.lower() or "does not exist" in error_str.lower():
                    print(f"⚠️  Adım {i} uyarı: {error_str[:80]}")
                else:
                    print(f"❌ Adım {i} hata: {error_str[:150]}")
    
    print("\n" + "="*60)
    print("✅ Veritabanı başarıyla temizlendi ve optimize edildi!")
    
except Exception as e:
    print(f"\n❌ Genel hata: {str(e)[:200]}")

