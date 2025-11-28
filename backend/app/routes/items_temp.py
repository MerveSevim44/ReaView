from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, func
from ..database import get_db
from .. import models, schemas
from ..services.external_api import get_tmdb_reviews, get_google_books_reviews

router = APIRouter()


def calculate_hybrid_rating(item_id: int, item: models.Item, db: Session):
    """
    İçerik için hybrid rating hesapla:
    - external_rating: API'den gelen rating
    - user_rating: Kullanıcı reviews'lerinden
    - combined_rating: İkisinin ortalaması
    """
    rating_query = text("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings
        FROM reviews
        WHERE item_id = :item_id AND rating IS NOT NULL
    """)
    rating_result = db.execute(rating_query, {"item_id": item_id}).first()
    
    user_rating_from_reviews = rating_result[0] or 0
    review_count = rating_result[1] or 0
    
    ratings_query = text("""
        SELECT AVG(score) as avg_score, COUNT(*) as total_ratings
        FROM ratings
        WHERE item_id = :item_id
    """)
    ratings_result = db.execute(ratings_query, {"item_id": item_id}).first()
    
    user_rating_from_ratings = ratings_result[0] or 0
    ratings_count = ratings_result[1] or 0
    
    total_rating_count = review_count + ratings_count
    
    if total_rating_count > 0:
        user_rating = round((user_rating_from_reviews * review_count + user_rating_from_ratings * ratings_count) / total_rating_count, 1)
    else:
        user_rating = 0
    
    external_rating = item.external_rating or 0
    
    if external_rating > 0 and user_rating > 0:
        combined_rating = round((external_rating + user_rating) / 2, 1)
    elif external_rating > 0:
        combined_rating = external_rating
    else:
        combined_rating = user_rating
    
    return {
        "external_rating": external_rating,
        "user_rating": user_rating,
        "combined_rating": combined_rating,
        "review_count": total_rating_count,
        "popularity": total_rating_count
    }


# ============ LIBRARY ENDPOINTS (SABİT ROUTES - EN BAŞTA) ============

@router.get("/library/{user_id}")
def get_user_library(user_id: int, status: str = Query(None), db: Session = Depends(get_db)):
    """Kullanıcının kütüphanesini getir"""
    try:
        query = db.query(models.UserLibrary).filter(
            models.UserLibrary.user_id == user_id
        )
        
        if status:
            query = query.filter(models.UserLibrary.status == status)
        
        library_entries = query.all()
        
        items = []
        for entry in library_entries:
            item = db.query(models.Item).filter(models.Item.item_id == entry.item_id).first()
            if item:
                items.append({
                    "library_id": entry.library_id,
                    "item_id": entry.item_id,
                    "status": entry.status,
                    "title": item.title,
                    "item_type": item.item_type,
                    "poster_url": item.poster_url,
                    "added_at": entry.added_at
                })
        
        return {
            "success": True,
            "user_id": user_id,
            "status_filter": status,
            "items": items,
            "total": len(items)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{item_id}/library")
def add_to_library(item_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """Kullanıcının kütüphanesine içerik ekle/çıkar"""
    try:
        user_id = data.get("user_id")
        status = data.get("status")
        action = data.get("action", "add")
        
        if not user_id or not status:
            raise HTTPException(status_code=400, detail="user_id ve status gerekli")
        
        if status not in ['read', 'toread', 'watched', 'towatch']:
            raise HTTPException(status_code=400, detail="Geçersiz status")
        
        item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="İçerik bulunamadı")
        
        if action == "add":
            existing_entry = db.query(models.UserLibrary).filter(
                models.UserLibrary.user_id == user_id,
                models.UserLibrary.item_id == item_id
            ).first()
            
            if existing_entry:
                if existing_entry.status == status:
                    return {
                        "success": True,
                        "message": "Bu status zaten kütüphanede var",
                        "item_id": item_id,
                        "status": status,
                        "library_id": existing_entry.library_id,
                        "action": "add"
                    }
                
                existing_entry.status = status
                db.commit()
                db.refresh(existing_entry)
                
                return {
                    "success": True,
                    "message": f"Status '{status}' olarak güncellendi",
                    "item_id": item_id,
                    "status": status,
                    "library_id": existing_entry.library_id,
                    "action": action
                }
            else:
                library_entry = models.UserLibrary(
                    user_id=user_id,
                    item_id=item_id,
                    status=status
                )
                db.add(library_entry)
                db.commit()
                db.refresh(library_entry)
                
                return {
                    "success": True,
                    "message": f"Status '{status}' olarak eklendi",
                    "item_id": item_id,
                    "status": status,
                    "library_id": library_entry.library_id,
                    "action": action
                }
        
        elif action == "remove":
            deleted = db.query(models.UserLibrary).filter(
                models.UserLibrary.user_id == user_id,
                models.UserLibrary.item_id == item_id,
                models.UserLibrary.status == status
            ).delete()
            db.commit()
            
            return {
                "success": True,
                "message": f"İçerik kütüphaneden kaldırıldı",
                "item_id": item_id,
                "status": status,
                "action": action,
                "deleted_count": deleted
            }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ CUSTOM LISTS ENDPOINTS (SABİT ROUTES) ============

@router.get("/custom-lists/{user_id}")
def get_custom_lists(user_id: int, db: Session = Depends(get_db)):
    """Kullanıcının tüm özel listelerini getir"""
    try:
        lists = db.query(models.CustomList).filter(
            models.CustomList.user_id == user_id
        ).all()
        
        custom_lists = []
        for lst in lists:
            items = db.query(models.ListItem).filter(
                models.ListItem.list_id == lst.list_id
            ).count()
            
            custom_lists.append({
                "list_id": lst.list_id,
                "name": lst.name,
                "description": lst.description,
                "is_public": lst.is_public,
                "item_count": items,
                "created_at": lst.created_at,
                "updated_at": lst.updated_at
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "lists": custom_lists,
            "total": len(custom_lists)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/custom-lists")
def create_custom_list(data: dict = Body(...), db: Session = Depends(get_db)):
    """Kullanıcının listesi oluştur"""
    try:
        user_id = data.get("user_id")
        name = data.get("name")
        description = data.get("description", "")
        is_public = data.get("is_public", 0)
        
        if not user_id or not name:
            raise HTTPException(status_code=400, detail="user_id ve name gerekli")
        
        new_list = models.CustomList(
            user_id=user_id,
            name=name,
            description=description,
            is_public=is_public
        )
        db.add(new_list)
        db.commit()
        db.refresh(new_list)
        
        return {
            "success": True,
            "message": "Liste oluşturuldu",
            "list_id": new_list.list_id,
            "name": new_list.name
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/custom-lists/{list_id}")
def delete_custom_list(list_id: int, db: Session = Depends(get_db)):
    """Özel listeyi sil"""
    try:
        custom_list = db.query(models.CustomList).filter(
            models.CustomList.list_id == list_id
        ).first()
        
        if not custom_list:
            raise HTTPException(status_code=404, detail="Liste bulunamadı")
        
        db.query(models.ListItem).filter(
            models.ListItem.list_id == list_id
        ).delete()
        
        db.delete(custom_list)
        db.commit()
        
        max_list_id = db.query(func.max(models.CustomList.list_id)).scalar()
        if max_list_id is None:
            db.execute(text("SELECT setval('lists_list_id_seq', 1, false)"))
        else:
            db.execute(text(f"SELECT setval('lists_list_id_seq', {max_list_id}, true)"))
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Liste silindi (ID: {list_id})",
            "list_id": list_id
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ SEARCH & FEATURED ENDPOINTS ============

@router.get("/search", response_model=list[schemas.ItemOut])
def search_items(
    q: str = Query(..., min_length=2, description="Arama metni"),
    item_type: str = Query(None, description="'book' veya 'movie'"),
    db: Session = Depends(get_db)
):
    """İçerik ara"""
    query = db.query(models.Item)
    
    query = query.filter(
        (models.Item.title.ilike(f"%{q}%")) |
        (models.Item.description.ilike(f"%{q}%"))
    )
    
    if item_type:
        query = query.filter(models.Item.item_type == item_type)
    
    items = query.limit(20).all()
    
    result = []
    for item in items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


@router.get("/featured/top-rated", response_model=list[schemas.ItemOut])
def get_top_rated(limit: int = Query(6, ge=1, le=50), db: Session = Depends(get_db)):
    """En yüksek puanlı içerikleri getir"""
    all_items = db.query(models.Item).all()
    
    items_with_ratings = []
    for item in all_items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        combined = rating_info.get('combined_rating', 0)
        items_with_ratings.append((item, rating_info, combined))
    
    items_with_ratings.sort(key=lambda x: x[2], reverse=True)
    top_items = items_with_ratings[:limit]
    
    result = []
    for item, rating_info, _ in top_items:
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


@router.get("/featured/popular", response_model=list[schemas.ItemOut])
def get_popular(limit: int = Query(6, ge=1, le=50), db: Session = Depends(get_db)):
    """En popüler içerikleri getir"""
    all_items = db.query(models.Item).all()
    
    items_with_scores = []
    for item in all_items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        review_count = rating_info.get('review_count', 0)
        combined_rating = rating_info.get('combined_rating', 0)
        
        if review_count > 0:
            popularity_score = (review_count * 2) + combined_rating
        else:
            popularity_score = combined_rating
        
        items_with_scores.append((item, rating_info, popularity_score, review_count))
    
    items_with_scores.sort(key=lambda x: (x[2], x[3]), reverse=True)
    top_items = items_with_scores[:limit]
    
    result = []
    for item, rating_info, _, _ in top_items:
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


# ============ DYNAMIC ROUTES (EN SONDA) ============

@router.get("/", response_model=list[schemas.ItemOut])
def get_items(db: Session = Depends(get_db), limit: int = 20):
    """Tüm içerikleri listele"""
    items = db.query(models.Item).limit(limit).all()
    
    result = []
    for item in items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


@router.post("/", response_model=schemas.ItemOut)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Yeni içerik ekle"""
    new_item = models.Item(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Tekil içerik detayları"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    rating_info = calculate_hybrid_rating(item.item_id, item, db)
    item_dict = {
        "item_id": item.item_id,
        "title": item.title,
        "description": item.description,
        "item_type": item.item_type,
        "year": item.year,
        "poster_url": item.poster_url,
        "external_api_id": item.external_api_id,
        "external_api_source": item.external_api_source,
        "genres": item.genres,
        "authors": item.authors,
        "director": item.director,
        "actors": item.actors,
        "page_count": item.page_count,
        "created_at": item.created_at,
        **rating_info
    }
    return item_dict


@router.put("/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: int, item_update: schemas.ItemCreate, db: Session = Depends(get_db)):
    """İçerik bilgilerini güncelle"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """İçerik sil"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    db.delete(item)
    db.commit()
    return {"message": "İçerik başarıyla silindi"}
