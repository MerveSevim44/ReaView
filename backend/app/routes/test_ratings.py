"""
Test endpoint'i: API'den rating verisi ile items ekle
POST /items/test-data
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter()

@router.post("/test-data")
def create_test_items_with_ratings(db: Session = Depends(get_db)):
    """Test için 4 item ekle (external_rating ile)"""
    
    test_items = [
        {
            "title": "Harry Potter ve Felsefe Taşı",
            "item_type": "book",
            "year": 2001,
            "description": "Sihir ve büyü dünyasına giriş.",
            "authors": "J.K. Rowling",
            "external_api_id": "hp1_book",
            "external_api_source": "google_books",
            "external_rating": 9,  # 0-10 skala
            "genres": "Fantastik, Macera"
        },
        {
            "title": "Dune",
            "item_type": "movie",
            "year": 2021,
            "description": "Arrakis çölünde geçen epik uzay operası.",
            "director": "Denis Villeneuve",
            "external_api_id": "dune_2021_tmdb",
            "external_api_source": "tmdb",
            "external_rating": 8,  # TMDB vote_average
            "genres": "Bilim Kurgu, Macera"
        },
        {
            "title": "The Great Gatsby",
            "item_type": "book",
            "year": 1925,
            "description": "Jazz Çağı'nda aşk ve zenginlik üzerine klasik roman.",
            "authors": "F. Scott Fitzgerald",
            "external_api_id": "gatsby_book",
            "external_api_source": "google_books",
            "external_rating": 8,  # Ölçeklendirilmiş (5.0 * 2)
            "genres": "Klasik, Drama"
        },
        {
            "title": "To Kill a Mockingbird",
            "item_type": "book",
            "year": 1960,
            "description": "Irkçılık ve adalet hakkında etkileyici bir hikaye.",
            "authors": "Harper Lee",
            "external_api_id": "mockingbird_book",
            "external_api_source": "openlibrary",
            "external_rating": 9,  # Ölçeklendirilmiş (4.5 * 2)
            "genres": "Klasik, Drama"
        }
    ]
    
    created_items = []
    for item_data in test_items:
        # Aynı item varsa skip et
        existing = db.query(models.Item).filter(
            models.Item.external_api_id == item_data["external_api_id"]
        ).first()
        
        if not existing:
            new_item = models.Item(**item_data)
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            created_items.append({
                "item_id": new_item.item_id,
                "title": new_item.title,
                "external_rating": new_item.external_rating
            })
    
    return {
        "message": f"{len(created_items)} test item'i eklendi",
        "items": created_items
    }
