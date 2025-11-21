from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from typing import Optional

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Authorization header'dan token al ve kullanıcıyı getir
    Token format: "Bearer token_user_id_random"
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header gereklidir",
        )
    
    try:
        # "Bearer token_123_abc" formatını parse et
        scheme, token = authorization.split(" ")
        
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz authentication scheme",
            )
        
        # Token'ı parse et: "token_<user_id>_<random>"
        parts = token.split("_")
        if len(parts) < 2 or parts[0] != "token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz token formatı",
            )
        
        user_id = int(parts[1])
        
        # Kullanıcıyı veritabanından al
        user = db.query(models.User).filter(
            models.User.user_id == user_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kullanıcı bulunamadı",
            )
        
        return user
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz token",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
