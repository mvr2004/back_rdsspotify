from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import spotify
from app.core.config import settings
from app.api import auth

# Create FastAPI application
app = FastAPI(
    title="RDS Spotify Backend",
    description="API for Spotify statistics and smart playlists",
    version="1.0.0"
)

# Configure CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Spotify routes
app.include_router(
    spotify.router,
    prefix="/api/spotify",
    tags=["spotify"]
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["auth"]
)


# Include callback redirect route
from app.api import callback
app.include_router(
    callback.router,
    prefix="/auth",
    tags=["auth-redirect"]
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to RDS Spotify API",
        "docs": "/docs",
        "endpoints": {
            "token_health": "/api/spotify/token",
            "dashboard_profile": "/api/spotify/me/profile",
            "test": "/api/spotify/test",
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "spotify-api"}
