"""
Vercel serverless function entry point for FastAPI app
"""
import sys
from pathlib import Path

# Add the project root to Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import app components
from backend.app.routes import auth, items, reviews, feed, users, external, follows, likes, ratings, lists, comments

app = FastAPI(title="ReaView API")

# === CORS CONFIGURATION (MUST be FIRST - before routes) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Skip database initialization in serverless - migrations should be pre-run
# Initialize database on startup (only once in serverless)
@app.on_event("startup")
def startup_event():
    print("[OK] Application started on Vercel")
    # Skip migrations in serverless environment
    # Ensure your database is already migrated before deployment

# Mount avatars directory as static files (if exists)
avatars_dir = Path(__file__).parent.parent / "backend" / "avatars"
if avatars_dir.exists():
    try:
        app.mount("/avatars", StaticFiles(directory=str(avatars_dir)), name="avatars")
    except Exception as e:
        print(f"[WARNING] Could not mount avatars directory: {e}")

# Include routers from route modules
routers_config = [
    (auth, "/auth", "Auth"),
    (items, "/items", "Items"),
    (reviews, "/reviews", "Reviews"),
    (feed, "/feed", "Feed"),
    (users, "/users", "Users"),
    (external, "/external", "External API"),
    (follows, "/users", "Follow System"),
    (likes, "/likes", "Likes"),
    (ratings, "/ratings", "Ratings"),
    (lists, "/lists", "Lists"),
    (comments, "/comments", "Comments"),
]

for module, prefix, tag in routers_config:
    try:
        if hasattr(module, "router"):
            app.include_router(module.router, prefix=prefix, tags=[tag])
    except Exception as e:
        print(f"[WARNING] Could not load router {tag}: {e}")

# Health check endpoint
@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "[OK] ReaView API is running on Vercel"}

# Export the app for Vercel
app = app
