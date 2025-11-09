from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# .env dosyasından DATABASE_URL değişkenini al
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# PostgreSQL bağlantısı (Neon bağlantı string'in ?sslmode=require içermeli)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency (route içinde kullanmak için)
def get_db():
    db = SessionLocal()
    try:
        
        yield db
    finally:
        db.close()
