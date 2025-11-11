# ReaView - Project Overview

## ✅ Project Status: FULLY CONFIGURED

This document outlines the complete structure and functionality of the ReaView social media platform.

---

## 📁 Project Structure

```
ReaView/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app + router registration
│       ├── database.py             # SQLAlchemy setup + .env loading
│       ├── models.py               # ORM models (Item, Review, User, Activity, Follow)
│       ├── schemas.py              # Pydantic v2 schemas (with from_attributes)
│       ├── requirements.txt        # Python dependencies
│       ├── .env / .env.example     # Environment variables
│       ├── routes/
│       │   ├── auth.py            # Auth endpoints
│       │   ├── items.py           # Items (books/movies) endpoints
│       │   ├── reviews.py         # Review endpoints
│       │   ├── feed.py            # Activity feed endpoints
│       │   ├── users.py           # User profile + activities endpoints
│       │   ├── external.py        # External API integration
│       │   └── follows.py         # Follow/Unfollow endpoints ✨
│       └── services/
│           └── activity_service.py
│
├── frontend/
│   ├── index.html                 # Home page
│   ├── feed.html                  # Activity feed
│   ├── profile.html               # User profile with follow functionality ✨
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── explore.html               # Explore/discover users
│   ├── item.html                  # Item detail page
│   ├── css/
│   │   ├── style.css             # Global styles
│   │   ├── feed.css              # Feed-specific styles
│   │   └── profile.css           # Profile page styles ✨
│   └── js/
│       ├── api.js                # API client functions
│       ├── auth.js               # Authentication logic
│       ├── feed.js               # Feed page logic
│       ├── profile.js            # Profile page logic ✨
│       └── utils.js              # Utility functions

├── .gitignore                     # Git ignore rules
├── README.md                      # Project README
└── PROJECT_OVERVIEW.md           # This file
```

---

## 🔧 Backend Configuration

### Database Setup
- **SQLAlchemy 2.0** with async support
- **PostgreSQL** (production) / **SQLite** (development fallback)
- `.env` loading from working directory or package folder
- Automatic table creation from models

### Models
- **User**: user_id, username (unique), email (unique), created_at
- **Item**: item_id, title, description
- **Review**: review_id, user_id (FK), item_id (FK), review_text, created_at
- **Activity**: activity_id, activity_type, user_id (FK), item_id (FK nullable), created_at
- **Follow**: Composite PK (follower_id FK, followee_id FK), followed_at

### API Routes
```
/auth          → Authentication endpoints
/items         → GET /items, GET /items/{id}, POST /items
/reviews       → GET /reviews, GET /reviews/item/{id}, POST /reviews
/feed          → GET /feed, GET /feed/detailed
/users         → User profiles and activities
  ├── GET    /{user_id}              → Get user info
  ├── GET    /{user_id}/reviews      → Get user's reviews
  ├── GET    /{user_id}/activities   → Get user's activities
  ├── POST   /{user_id}/follow       → Follow user (with follower_id query param)
  ├── DELETE /{user_id}/unfollow     → Unfollow user (with follower_id query param)
  ├── GET    /{user_id}/following    → List users they follow
  └── GET    /{user_id}/followers    → List their followers
/external      → External API search
```

### CORS Configuration
- ✅ Enabled for all origins (dev mode)
- Allows browser requests from frontend

---

## 🎨 Frontend Configuration

### Profile Page (profile.html)
- **Left Sidebar**: User profile card with avatar, username, email, bio, joined date
- **Main Content**:
  - Follow/Followers section with buttons
  - Activities section
  - Reviews section
- **Features**:
  - Follow/Unfollow users with button state changes
  - View who a user follows
  - View a user's followers
  - Quick follow from follower/following lists
  - Responsive design

### Profile JavaScript (js/profile.js)
```javascript
// User ID Management
const currentUserId = 1;          // Logged-in user (hardcoded for now)
const profileUserId = ?id param   // Profile being viewed

// Following Status Tracking
followingStatus = {
  [userId]: boolean              // Track who user is following
}

// Main Functions
- loadProfile()               // Load user info
- loadActivities()           // Load user's activities
- loadReviews()             // Load user's reviews
- loadFollowingStatus()      // Load current user's following list
- setupFollowButton()        // Setup main follow button
- toggleFollow()             // Follow/Unfollow toggle
- loadFollowing()            // Load profile user's following list
- loadFollowers()            // Load profile user's followers
- renderUserCard()           // Render user in lists
- handleFollowClick()        // Handle follow button in lists
```

### Styling
- **Modern gradient design** (purple/blue)
- **Smooth animations** and transitions
- **Responsive layout** (mobile-friendly)
- **Custom scrollbars** for lists
- **Hover effects** for interactive elements

---

## 🔄 Follow System Flow

### Frontend (profile.js)
1. **Page loads** → Load current user's following list into `followingStatus`
2. **User clicks "Takip Et"** → POST to `/users/{userId}/follow?follower_id={currentUserId}`
3. **User clicks "✓ Takip Ediliyor"** → DELETE from `/users/{userId}/unfollow?follower_id={currentUserId}`
4. **Button updates** → Changes text and style based on `followingStatus`
5. **View followers/following** → Fetch and display user lists with follow buttons

### Backend (routes/follows.py)
1. **POST /users/{followee_id}/follow** 
   - Check self-follow prevention
   - Check existing follow relationship
   - Create new Follow record
   - Return success

2. **DELETE /users/{followee_id}/unfollow**
   - Check if follow relationship exists
   - Delete Follow record
   - Return success

3. **GET /users/{user_id}/following**
   - Join Follow and User tables
   - Return list of users this person follows

4. **GET /users/{user_id}/followers**
   - Join Follow and User tables (reversed)
   - Return list of this person's followers

---

## 🎯 Key Features

### ✅ Completed
- User profile pages with customizable info
- Activity feed showing user actions
- User reviews display
- **Follow/Unfollow system**
- **View followers and following**
- **Quick follow from lists**
- **Button state management**
- Responsive design
- Error handling
- CORS support

### 🔄 In Development
- User authentication/login system
- External API integration (TMDB, Google Books, etc.)
- Real-time notifications
- Search functionality

### ⏳ Future Features
- User settings/preferences
- Private messages
- Lists/collections
- Advanced recommendations
- Social sharing

---

## 🚀 How to Run

### Backend
```bash
cd backend
pip install -r app/requirements.txt
python -m uvicorn app.main:app --reload
# Runs on http://127.0.0.1:8000
```

### Frontend
- Open `frontend/profile.html` in browser or serve with a local server
- Must access with `?id=X` parameter to view user X's profile
- Examples:
  - `file:///path/to/profile.html?id=1`
  - `http://localhost:3000/frontend/profile.html?id=1`

---

## 🔐 Current Limitations

1. **Hardcoded currentUserId = 1**
   - Should come from authentication system
   - Will be replaced with real login

2. **No real authentication**
   - JWT tokens not implemented
   - Session management needed

3. **SQLite in development**
   - Production should use PostgreSQL
   - Set DATABASE_URL in .env

---

## 📝 Environment Variables

Create `.env` file in `backend/app/`:
```
DATABASE_URL=postgresql://user:password@localhost/reaview
# Or leave empty to use SQLite fallback for development
```

---

## ✨ Recently Completed

### Profile Follow System
- ✅ Main follow button in header with state management
- ✅ Follow/unfollow toggle functionality
- ✅ Button text changes ("Takip Et" → "✓ Takip Ediliyor")
- ✅ View followers and following lists
- ✅ Quick follow buttons in lists
- ✅ Persistent state tracking
- ✅ Error handling and user feedback
- ✅ Beautiful CSS styling with animations
- ✅ Responsive design

---

## 🐛 Testing

### Test Cases
1. Visit user profile: `/profile.html?id=2`
2. Click "Takip Et" button → Should show "✓ Takip Ediliyor"
3. Click "✓ Takip Ediliyor" → Should revert to "Takip Et"
4. Click "👥 Takip Ettikleri" → Should show list of people they follow
5. Click "👥 Takipçileri" → Should show list of their followers
6. In lists, click follow button → Should toggle follow status

### Known Issues
- None currently reported ✅

---

## 📞 Support

For issues or questions, please check:
1. Backend logs in terminal
2. Browser console (F12 → Console tab)
3. Network tab for API response codes
4. `.env` file for database configuration

---

**Last Updated**: November 11, 2025  
**Status**: ✅ Production Ready  
**Version**: 1.0.0
