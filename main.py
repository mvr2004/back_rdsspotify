from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import spotify
from app.core.config import settings
from app.api import auth
from app.api.auth import router as auth_router



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
            "token": "/api/spotify/token",
            "test": "/api/spotify/test"
        }
    }
    
@app.get("/auth/callback")
async def auth_callback_redirect():
    """Redirect from Spotify to our API callback"""
    from fastapi.responses import RedirectResponse
    import urllib.parse
    
    # Get current query parameters
    import requests
    from starlette.requests import Request
    
    # This would need request context, so let's create a proper endpoint
    
    return {"message": "Please use /api/auth/callback instead"}
    
    

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "spotify-api"}