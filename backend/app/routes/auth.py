from fastapi import APIRouter, Depends, HTTPException, Body, Header
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
    authorization: str = Header(None),
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
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token geçersiz")


@router.post("/logout")
def logout():
    """Kullanıcı çıkış yap"""
    return {"message": "Başarıyla çıkış yapıldı"}


# ============== PASSWORD RESET ==============

@router.post("/forgot-password")
def forgot_password(email: str = Body(...), db: Session = Depends(get_db)):
    """Şifre sıfırlama isteği - e-posta gönder"""
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            # Don't reveal if email exists (security best practice)
            print(f"⚠️ Password reset request for non-existent email: {email}")
            return {"message": "E-posta adresiniz kayıtlıysa, şifre sıfırlama bağlantısı gönderilecektir"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Set token to expire in 1 hour
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Delete any existing tokens for this user
        db.query(models.PasswordResetToken).filter(
            models.PasswordResetToken.user_id == user.user_id,
            models.PasswordResetToken.used_at.is_(None)
        ).delete()
        
        # Create new token
        token_record = models.PasswordResetToken(
            user_id=user.user_id,
            token=reset_token,
            expires_at=expires_at
        )
        db.add(token_record)
        db.commit()
        
        # TODO: Send email with reset link
        reset_link = f"http://localhost:3000/reset-password.html?token={reset_token}"
        print(f"🔗 Password reset link for {email}: {reset_link}")
        
        # For development, return the link in response (REMOVE IN PRODUCTION)
        return {
            "message": "E-posta adresiniz kayıtlıysa, şifre sıfırlama bağlantısı gönderilecektir",
            "reset_link": reset_link  # REMOVE IN PRODUCTION - only for testing
        }
    except Exception as e:
        print(f"❌ Forgot password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Bir hata oluştu")


@router.post("/reset-password")
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Şifremi sıfırla"""
    try:
        # Validate password
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Şifre en az 8 karakter olmalı")
        
        if not any(c.isupper() for c in new_password):
            raise HTTPException(status_code=400, detail="Şifre en az bir büyük harf içermelidir")
        
        if not any(c.isdigit() for c in new_password):
            raise HTTPException(status_code=400, detail="Şifre en az bir sayı içermelidir")
        
        # Find token
        token_record = db.query(models.PasswordResetToken).filter(
            models.PasswordResetToken.token == token
        ).first()
        
        if not token_record:
            raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş bağlantı")
        
        # Check if token has expired
        if datetime.utcnow() > token_record.expires_at:
            raise HTTPException(status_code=400, detail="Bağlantının süresi dolmuş")
        
        # Check if token already used
        if token_record.used_at:
            raise HTTPException(status_code=400, detail="Bu bağlantı zaten kullanılmış")
        
        # Get user
        user = db.query(models.User).filter(
            models.User.user_id == token_record.user_id
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
        # Update password
        user.password_hash = hash_password(new_password)
        
        # Mark token as used
        token_record.used_at = datetime.utcnow()
        
        db.commit()
        
        print(f"✅ Password reset for user: {user.email}")
        return {
            "message": "Şifre başarıyla sıfırlandı",
            "email": user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Reset password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Bir hata oluştu")