# 📚 ReaView (BiblioNet)

<p align="center">
  <strong>Kitap ve Film İnceleme, Puanlama & Sosyal Keşif Platformu</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=FastAPI&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg?style=flat" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/PostgreSQL-Ready-336791.svg?style=flat&logo=PostgreSQL&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Frontend-Vanilla%20JS%20%7C%20CSS3-F7DF1E.svg?style=flat&logo=javascript&logoColor=black" alt="Frontend" />
  <img src="https://img.shields.io/badge/Deploy-Vercel-black.svg?style=flat&logo=vercel&logoColor=white" alt="Vercel" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat" alt="License" />
</p>

---

## 🌟 Proje Hakkında

**ReaView (BiblioNet)**; kitap ve sinema severleri bir araya getiren modern bir sosyal inceleme ve takip platformudur. Kullanıcılar binlerce kitap ve filmi keşfedebilir, puanlayıp detaylı incelemeler yazabilir, kişisel kütüphanelerini ("Okudum", "İzledim", "Okunacak", "İzlenecek") ve özel listelerini yönetebilir, diğer kullanıcıları takip ederek sosyal akış üzerinden etkileşimde bulunabilirler.

---

## ✨ Temel Özellikler

### 🔍 1. Kapsamlı İçerik Keşfi (Kitap & Film)
- **TMDb Entegrasyonu**: Popüler ve vizyondaki filmler, film detayları, yönetmen, oyuncu kadrosu ve afişler.
- **Google Books & OpenLibrary Entegrasyonu**: Milyonlarca kitap, yazar bilgileri, sayfa sayıları, türler ve kitap kapakları.
- Gelişmiş arama, türe ve yıla göre filtreleme imkanı.

### ⭐ 2. İnceleme & Puanlama Sistemi
- **1-10 Puanlama**: Kitap ve filmlere puan verme ve ortalama puanları görüntüleme.
- **Detaylı İncelemeler**: İçerikler hakkında uzun incelemeler yazabilme.
- **Etkileşim**: İncelemeleri beğenme, beğenenleri modal üzerinde listeleme ve incelemelere alt yorumlar ekleme.

### 📚 3. Kişisel Kütüphane & Özel Listeler
- **Durum Takibi**: *Okudum*, *Okunacak*, *İzledim*, *İzlenecek* kütüphane etiketleri.
- **Özel Koleksiyonlar / Listeler**: Özel başlık ve açıklamalarla tematik listeler oluşturma.
- **Gizlilik Düzeyleri**: Listeleri *Gizli (Private)*, *Sadece Takipçiler (Followers)* veya *Herkese Açık (Public)* olarak ayarlayabilme.

### 👥 4. Sosyal Akış & Takip Mekanizması
- Kullanıcıları takip etme ve takipten çıkma (Follow/Unfollow).
- **Dinamik Aktivite Akışı (Feed)**: Takip edilen kullanıcıların yeni incelemeleri, puanlamaları ve beğenilerini gerçek zamanlı takip etme.
- Zengin kullanıcı profilleri: Biyografi, avatar, takipçi/takip edilen sayıları, aktiviteler ve kütüphane istatistikleri.

### 🔐 5. Güvenlik & Hesap Yönetimi
- JWT (JSON Web Token) ve Bcrypt ile güvenli parola hashleme.
- Şifre sıfırlama (Forgot / Reset Password token mekanizması).
- Profil düzenleme, özel avatar yükleme/seçme ve kullanıcı ayarları.

---

## 🛠️ Teknoloji Yığını

| Katman | Teknolojiler |
|---|---|
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy, Pydantic, Uvicorn, Bcrypt, PyJWT |
| **Veritabanı** | PostgreSQL (Canlı/Prod), SQLite (Yerel Test) |
| **Frontend** | Vanilla HTML5, Modern CSS3 (CSS Variables, Flexbox/Grid, Responsive), Vanilla JavaScript (ES6 Modülleri) |
| **Harici API Entegrasyonları** | TMDb (The Movie Database) API, Google Books API, OpenLibrary API |
| **Dağıtım (Deployment)** | Vercel (Serverless Python Backend & Static Frontend) |

---

## 📂 Proje Dizin Yapısı

```text
ReaView/
├── api/
│   └── index.py             # Vercel Serverless Function giriş noktası
├── backend/
│   ├── app/
│   │   ├── routes/          # API Route modülleri (auth, items, reviews, feed, users, vb.)
│   │   ├── services/        # Dış servisler (TMDb, Google Books, E-posta vb.)
│   │   ├── database.py      # SQLAlchemy DB bağlantısı ve Session yönetimi
│   │   ├── models.py        # Veritabanı ORM modelleri
│   │   ├── schemas.py       # Pydantic doğrulama şemaları
│   │   └── main.py          # FastAPI ana uygulama dosyası
│   ├── avatars/             # Kullanıcı profil fotoğrafları
│   └── migrations/          # SQL migrasyon betikleri
├── frontend/
│   ├── css/                 # Sayfa ve bileşen stilleri
│   ├── js/
│   │   ├── components/      # Ortak bileşenler (navbar vb.)
│   │   ├── core/            # API yapılandırması, auth ve session yönetimi
│   │   ├── pages/           # Sayfalara özel mantıklar (feed, profile, explore vb.)
│   │   └── utils/           # Yardımcı fonksiyonlar ve formatlayıcılar
│   ├── index.html           # Giriş/Karşılama sayfası
│   ├── feed.html            # Sosyal aktivite akışı
│   ├── explore.html         # Kitap/Film arama ve keşif
│   ├── items.html           # İçerik detay ve inceleme sayfası
│   ├── profile.html         # Kullanıcı profil sayfası
│   ├── settings.html        # Hesap ayarları sayfası
│   ├── login.html           # Giriş yapma sayfası
│   └── register.html        # Kayıt olma sayfası
├── requirements.txt         # Python bağımlılıkları
├── run.bat                  # Windows tek tıkla başlatma betiği
├── run.ps1                  # PowerShell başlatma betiği
├── vercel.json              # Vercel yapılandırması
└── README.md                # Proje dokümantasyonu
```

---

## 🚀 Kurulum ve Yerel Çalıştırma

### Gereksinimler
- Python 3.10 veya üzeri
- Git
- *(Opsiyonel)* PostgreSQL (varsayılan olarak SQLite ile de test edilebilir)

### 1. Projeyi Klonlayın
```bash
git clone https://github.com/MerveSevim44/ReaView.git
cd ReaView
```

### 2. Sanal Ortam Oluşturun ve Bağımlılıkları Yükleyin
```bash
# Sanal ortam oluşturma
python -m venv venv

# Sanal ortamı aktifleştirme (Windows)
.\venv\Scripts\activate

# Sanal ortamı aktifleştirme (macOS/Linux)
source venv/bin/activate

# Bağımlılıkları yükleme
pip install -r requirements.txt
```

### 3. Çevre Değişkenlerini Yapılandırın
`backend/app/` dizini altında `.env` dosyası oluşturun:
```env
# Veritabanı (PostgreSQL veya yerel SQLite)
DATABASE_URL=sqlite:///./dev.db
# PostgreSQL örneği:
# DATABASE_URL=postgresql+psycopg2://kullanici:sifre@localhost:5432/reaview_db

# TMDb API Anahtarı (Film verileri için)
API_KEY=your_tmdb_api_key_here

# JWT Güvenlik Anahtarı
SECRET_KEY=your_super_secret_jwt_key
```

### 4. Tek Tıkla Başlatma (Windows)
Projeyi hem Backend (`http://localhost:8000`) hem Frontend (`http://localhost:8080`) ile birlikte tek seferde başlatmak için:
```cmd
run.bat
```
veya PowerShell ile:
```powershell
.\run.ps1
```

### 5. Manuel Olarak Başlatma

#### Backend'i Başlatma:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- API Dokümantasyonu (Swagger UI): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Frontend'i Başlatma:
```bash
cd frontend
python -m http.server 8080
```
- Tarayıcıda açın: `http://localhost:8080`

---

## 🔌 API Uç Noktaları Genel Bakış

| Modül | Prefix | Açıklama |
|---|---|---|
| **Auth** | `/auth` | Kayıt olma, giriş, şifremi unuttum, şifre sıfırlama |
| **Items** | `/items` | Kitap ve film listeleme, filtreleme, kütüphane işlemleri, detaylar |
| **Reviews** | `/reviews` | İnceleme oluşturma, düzenleme, silme, listeleme |
| **Feed** | `/feed` | Takip edilen kullanıcıların aktivitelerini listeleme |
| **Users** | `/users` | Kullanıcı profili, arama, biyografi/avatar güncelleme, takip işlemleri |
| **Likes** | `/likes` | İnceleme ve içerik beğenileri, beğenen kullanıcı listesi |
| **External** | `/external` | TMDb ve Google Books API doğrudan arama servisleri |
| **Health** | `/health` | API sağlık kontrolü |

---

## 🌐 Canlıya Alma (Deployment)

Proje Vercel üzerinde tek bir monorepo olarak veya ayrı ayrı dağıtılmak üzere yapılandırılmıştır:

1. **Vercel CLI** ile dağıtmak için:
   ```bash
   npm i -g vercel
   vercel --prod
   ```
2. Vercel panelinde `DATABASE_URL`, `API_KEY` ve `SECRET_KEY` ortam değişkenlerini tanımlayın.
3. Detaylı canlıya alma yönergeleri için [VERCEL_DEPLOYMENT.md](file:///c:/Users/merve/Desktop/ReaView/ReaView/VERCEL_DEPLOYMENT.md) ve [FRONTEND_DEPLOYMENT.md](file:///c:/Users/merve/Desktop/ReaView/ReaView/FRONTEND_DEPLOYMENT.md) dosyalarına göz atabilirsiniz.

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Detaylar için lisans dosyasına başvurabilirsiniz.
