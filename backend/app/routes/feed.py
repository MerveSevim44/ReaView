from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router = APIRouter()
 

 # ÖNCEKİ KOD BLOĞUNDA SADECE USERİD = 1 OLANLAR GETİRLİRDİ, ŞİMDİ İSE İSTEĞE BAĞLI OLARAK USERID PARAMETRESİ ALINIYOR
@router.get("/")
def get_feed(
    db: Session = Depends(get_db),
    user_id: int = Query(None, description="Takip edilen kullanıcıların aktivitelerini getirmek için kullanıcı ID")
):
    # Eğer user_id belirtilmemişse -> herkesi getir
    if user_id is None:
        query = text("""
        SELECT a.activity_id, a.activity_type, a.created_at,
               u.username, i.title, i.item_type
        FROM activities a
        JOIN users u ON u.user_id = a.user_id
        LEFT JOIN items i ON i.item_id = a.item_id
        ORDER BY a.created_at DESC
        LIMIT 20
        """)
        result = db.execute(query).fetchall()
        return [dict(r._mapping) for r in result]

    # Eğer user_id belirtilmişse -> sadece takip ettiklerini getir
    else:
        query = text("""
        SELECT a.activity_id, a.activity_type, a.created_at,
               u.username, i.title, i.item_type
        FROM activities a
        JOIN users u ON u.user_id = a.user_id
        LEFT JOIN items i ON i.item_id = a.item_id
        WHERE a.user_id IN (
            SELECT followee_id FROM follows WHERE follower_id = :uid
        )
        ORDER BY a.created_at DESC
        LIMIT 20
        """)
        result = db.execute(query, {"uid": user_id}).fetchall()
        return [dict(r._mapping) for r in result]
