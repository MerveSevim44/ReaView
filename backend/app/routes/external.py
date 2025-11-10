from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.external_api import search_tmdb, search_google_books, search_openlibrary

router = APIRouter()

@router.get("/search")
def external_search(type: str = Query(..., regex="^(movie|book)$"), query: str = Query(..., min_length=2)):
    if type == "movie":
        return search_tmdb(query)
    elif type == "book":
        try:
            return search_google_books(query)
        except Exception:
            # fallback to OpenLibrary
            return search_openlibrary(query)


# 🔹 Yeni ekleme fonksiyonu
@router.post("/import")
def import_item(
    type: str = Query(..., regex="^(movie|book)$"),
    query: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    # 1. Dış API'den verileri çek
    if type == "movie":
        data = search_tmdb(query)
    else:
        try:
            data = search_google_books(query)
        except Exception:
            data = search_openlibrary(query)

    if not data:
        return {"message": "Hiç veri bulunamadı."}

    # 2. İlk sonucu seç (basit örnek)
    item = data[0]

    # 3. Eğer aynı başlıkta item varsa yeniden ekleme
    existing = db.query(models.Item).filter(models.Item.title == item["title"]).first()
    if existing:
        return {"message": "Bu içerik zaten veritabanında mevcut.", "item_id": existing.item_id}

    # 4. Yeni item ekle (matching Item model fields)
    new_item = models.Item(
        title=item.get("title", ""),
        description=item.get("description")
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {"message": "İçerik başarıyla eklendi.", "item": item, "item_id": new_item.item_id}