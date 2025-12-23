from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import spotify
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title="RDS Spotify Backend",
    description="API for Spotify statistics and smart playlists",
    version="1.0.0"
)

# Configure CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  #  Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],  # All methods: GET, POST, etc
    allow_headers=["*"],
)

# Include Spotify routes
app.include_router(
    spotify.router,
    prefix="/api/spotify",  # All routes start with /api/spotify
    tags=["spotify"]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to RDS Spotify API",
        "docs": "/docs",
        "endpoints": {
            "token": "/api/spotify/token",
            "test": "/api/spotify/test"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "spotify-api"}