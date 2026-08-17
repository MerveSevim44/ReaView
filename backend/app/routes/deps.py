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
    if not authorization or authorization.strip() in ["", "Bearer", "Bearer null", "Bearer undefined", "null", "undefined"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header gereklidir",
        )
    
    try:
        # "Bearer token_123_abc" formatını parse et
        parts = authorization.strip().split(" ")
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz authorization header formatı",
            )
        
        scheme, token = parts
        
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz authentication scheme",
            )
        
        if token in ["null", "undefined", ""]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Oturum açılmamış",
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
    
    except HTTPException:
        raise
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


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """
    Opsiyonel kullanıcı getirme:
    - Geçerli token varsa: models.User döner
    - Token yoksa / geçersizse / 'Bearer null' ise: None döner (hata fırlatmaz)
    """
    if not authorization or authorization.strip() in ["", "Bearer", "Bearer null", "Bearer undefined", "null", "undefined"]:
        return None
    
    try:
        parts = authorization.strip().split(" ")
        if len(parts) != 2:
            return None
        
        scheme, token = parts
        if scheme.lower() != "bearer" or token in ["null", "undefined", ""]:
            return None
        
        token_parts = token.split("_")
        if len(token_parts) < 2 or token_parts[0] != "token":
            return None
        
        user_id = int(token_parts[1])
        user = db.query(models.User).filter(
            models.User.user_id == user_id
        ).first()
        return user
    except Exception:
        return None
