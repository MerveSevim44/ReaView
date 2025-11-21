#!/usr/bin/env python3
"""
Test verisi ekle - external_rating ile items
"""
import os
from dotenv import load_dotenv
from sqlalchemy import text, create_engine

load_dotenv('backend/app/.env')
db_url = os.getenv('DATABASE_URL')

if db_url:
    engine = create_engine(db_url)
    with engine.begin() as conn:
        # Test items ekle
        test_items = [
            ('Harry Potter ve Felsefe Taşı', 'book', 2001, 'Sihir ve büyü dünyasına giriş', 'J.K. Rowling', None, 'hp1_book', 'google_books', 9, 'Fantastik'),
            ('Dune', 'movie', 2021, 'Arrakis çölünde epik uzay operası', None, 'Denis Villeneuve', 'dune_2021', 'tmdb', 8, 'Bilim Kurgu'),
            ('The Great Gatsby', 'book', 1925, 'Jazz Çağında aşk ve zenginlik', 'F. Scott Fitzgerald', None, 'gatsby_book', 'google_books', 8, 'Klasik'),
            ('To Kill a Mockingbird', 'book', 1960, 'Irkçılık ve adalet hakkında', 'Harper Lee', None, 'mockingbird', 'openlibrary', 9, 'Klasik'),
        ]
        
        for title, item_type, year, desc, authors, director, api_id, api_source, rating, genre in test_items:
            sql = text('''
                INSERT INTO items (title, item_type, year, description, authors, director, 
                                  external_api_id, external_api_source, external_rating, genres, created_at)
                VALUES (:title, :item_type, :year, :desc, :authors, :director,
                       :api_id, :api_source, :rating, :genre, NOW())
                ON CONFLICT DO NOTHING
            ''')
            
            conn.execute(sql, {
                'title': title, 'item_type': item_type, 'year': year,
                'desc': desc, 'authors': authors, 'director': director,
                'api_id': api_id, 'api_source': api_source, 'rating': rating, 'genre': genre
            })
        
        print('✅ Test verisi başarıyla eklendi!')
        
        # Kontrol et
        result = conn.execute(text('SELECT COUNT(*) FROM items WHERE external_rating > 0'))
        count = result.scalar()
        print(f'📊 {count} item external_rating ile kayıtlı')
else:
    print('❌ DATABASE_URL bulunamadı')
