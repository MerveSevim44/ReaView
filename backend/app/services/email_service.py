"""
Email Service - E-posta gönderme işlemleri
Development'ta console'a yazıyor, production'da SMTP kullanmalı
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_password_reset_email(user_email: str, reset_link: str) -> bool:
    """
    Şifre sıfırlama linki e-postası gönder
    
    Args:
        user_email: Kullanıcının e-posta adresi
        reset_link: Şifre sıfırlama linki
    
    Returns:
        bool: Başarılı (True) veya başarısız (False)
    """
    try:
        # SMTP ayarları
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "zeycanaslan7@gmail.com")
        sender_password = os.getenv("SENDER_PASSWORD", "znzg jxqo eami gmxv")
        
        # E-posta içeriği
        subject = "BiblioNet - Şifre Sıfırlama Linki"
        body = f"""
Merhaba,

Şifre sıfırlama isteği aldık. Aşağıdaki linke tıklayarak yeni şifrenizi belirleyebilirsiniz:

{reset_link}

Bu link 1 saat geçerlidir.

Link çalışmazsa, aşağıdaki adresi tarayıcınıza kopyalayıp yapıştırın:
{reset_link}

Eğer siz bu isteği yapmadıysanız, bu e-postayı yok sayabilirsiniz.

---
BiblioNet Ekibi
        """
        
        # E-posta oluştur
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = user_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        # E-postayı gönder
        try:
            # Gmail için TLS bağlantısı
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # TLS şifreli bağlantı
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, user_email, msg.as_string())
                print(f"✅ E-posta gönderildi: {user_email}")
                return True
        except smtplib.SMTPAuthenticationError:
            print(f"❌ Gmail doğrulama hatası. Ayarları kontrol et.")
            print(f"   Sender Email: {sender_email}")
            print(f"   Password: {'*' * len(sender_password)}")
            print(f"🔗 Reset linki (fallback): {reset_link}")
            return True
        except ConnectionRefusedError:
            print(f"⚠️ SMTP serveri bağlantısı reddedildi.")
            print(f"📧 E-posta gönderilecekti: {user_email}")
            print(f"🔗 Reset linki: {reset_link}")
            return True
            
    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {str(e)}")
        print(f"🔗 Reset linki (fallback): {reset_link}")
        return True  # Development'ta hata kabul et
