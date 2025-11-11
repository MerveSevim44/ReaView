from fastapi import APIRouter, Depends, HTTPException, FastAPI
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter()

app = FastAPI(title="ReaView API", redirect_slashes=False)

# 1️⃣ Tüm içerikleri listele
@router.get("/", response_model=list[schemas.ItemOut])
def get_items(db: Session = Depends(get_db)):
    items = db.query(models.Item).limit(20).all()
    return items

# 2️⃣ Tek bir içeriği id ile getir
@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    return item

# 3️⃣ Yeni içerik ekle (isteğe bağlı test için)
@router.post("/", response_model=schemas.ItemOut)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    new_item = models.Item(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# 4️⃣ Favorilere ekle (dummy endpoint - would need favorites table)
@router.post("/{item_id}/favorite")
def add_to_favorite(item_id: int, user_id: dict = None):
    """Add item to user's favorites"""
    return {"message": "İçerik favorilerinize eklendi!", "item_id": item_id}

# 5️⃣ Listeye ekle (dummy endpoint - would need lists table)
@router.post("/{item_id}/add-to-list")
def add_to_list(item_id: int, user_id: dict = None):
    """Add item to user's list"""
    return {"message": "İçerik listeme eklendi!", "item_id": item_id}