from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import models, schemas
from ..database import get_db
from ..services.external_api import search_tmdb, search_google_books, search_openlibrary

router = APIRouter()


@router.get("/search")
def external_search(type: str = Query(..., regex="^(movie|book)$"), query: str = Query(..., min_length=2)):
    """Search external APIs for movies or books. Returns multiple results."""
    if type == "movie":
        return search_tmdb(query)
    elif type == "book":
        try:
            return search_google_books(query)
        except Exception:
            return search_openlibrary(query)


@router.post("/import")
def import_item(
    type: str = Query(..., regex="^(movie|book)$"),
    query: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """
    Fetch data from external APIs and save to database.
    - Searches external APIs for movies/books matching the query
    - Fetches enriched metadata (director, actors for movies; authors, pages for books)
    - Saves to items table with unique constraint (title, item_type)
    - Returns the first result or a message if no data found
    """
    # 1. Fetch data from external APIs
    if type == "movie":
        data = search_tmdb(query)
    else:
        try:
            data = search_google_books(query)
        except Exception:
            data = search_openlibrary(query)

    if not data:
        return {"message": "Hiç veri bulunamadı."}

    # 2. Take the first result
    first_result = data[0]

    # 3. Check if item already exists (by title + item_type)
    existing = db.query(models.Item).filter(
        models.Item.title == first_result["title"],
        models.Item.item_type == first_result["item_type"]
    ).first()
    
    if existing:
        return {
            "message": "Bu içerik zaten veritabanında mevcut.",
            "item_id": existing.item_id,
            "item": schemas.ItemOut.from_orm(existing)
        }

    # 4. Create new Item with all enriched metadata
    new_item = models.Item(
        title=first_result.get("title", "Unknown"),
        description=first_result.get("description", ""),
        item_type=first_result.get("item_type", "book"),
        year=first_result.get("year"),
        poster_url=first_result.get("poster_url"),
        genres=first_result.get("genres"),
        authors=first_result.get("authors"),  # For books
        page_count=first_result.get("page_count"),  # For books
        director=first_result.get("director"),  # For movies
        actors=first_result.get("actors"),  # For movies
        external_api_source=first_result.get("external_api_source"),
        external_api_id=first_result.get("external_api_id"),
        external_rating=first_result.get("external_rating", 0),
    )
    
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        return {
            "message": "İçerik başarıyla eklendi.",
            "item": schemas.ItemOut.from_orm(new_item),
            "item_id": new_item.item_id
        }
    except IntegrityError:
        db.rollback()
        return {"message": "Bu içerik zaten veritabanında mevcut (benzersiz kısıtlama)."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Veritabanı hatası: {str(e)}")