from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models, schemas
from datetime import datetime
import hashlib
import secrets

router = APIRouter()


# ============== HELPER FUNCTIONS ==============

def hash_password(password: str) -> str:
    """Şifreyi hash'le"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Hash'lenmiş şifreyi doğrula"""
    try:
        salt, pwd_hash = password_hash.split('$')
        pwd_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwd_check.hex() == pwd_hash
    except:
        return False


def generate_token(user_id: int) -> str:
    """JWT token oluştur"""
    token = secrets.token_urlsafe(32)
    return f"token_{user_id}_{token}"


# ============== AUTH ENDPOINTS ==============

@router.get("/ping")
async def ping():
    """Health endpoint for auth routes."""
    return {"service": "auth", "status": "ok"}


@router.post("/login")
def login(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Kullanıcı giriş yap"""
    # Kullanıcıyı e-posta ile bul
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-posta veya şifre yanlış")
    
    # Token oluştur
    token = generate_token(user.user_id)
    
    return {
        "user": {
            "user_id": user.user_id,
            "id": user.user_id,
            "username": user.username,
            "email": user.email
        },
        "token": token
    }


@router.post("/register")
def register(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Yeni kullanıcı kaydı"""
    # E-posta zaten kayıtlı mı?
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı")
    
    # Username zaten alınmış mı?
    existing_username = db.query(models.User).filter(models.User.username == username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış")
    
    # Yeni kullanıcı oluştur
    password_hash = hash_password(password)
    new_user = models.User(
        username=username,
        email=email,
        password_hash=password_hash,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Token oluştur
    token = generate_token(new_user.user_id)
    
    return {
        "user": {
            "user_id": new_user.user_id,
            "id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email
        },
        "token": token
    }


@router.get("/current-user")
def get_current_user(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Aktif kullanıcı bilgisini al"""
    # Authorization header'dan token çıkart
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token gerekli")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Token'dan user_id'yi çıkar
        parts = token.split('_')
        if len(parts) < 2:
            raise Exception("Invalid token format")
        
        user_id = int(parts[1])
        
        # Kullanıcıyı bul
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Token geçersiz")
        
        return {
            "user_id": user.user_id,
            "id": user.user_id,
            "username": user.username,
            "email": user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token geçersiz")


@router.post("/logout")
def logout():
    """Kullanıcı çıkış yap"""
    return {"message": "Başarıyla çıkış yapıldı"}