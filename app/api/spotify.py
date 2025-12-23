from fastapi import APIRouter, HTTPException
from app.services.spotify_service import SpotifyService

# Create a router (group of routes)
router = APIRouter()

@router.get("/token")
async def get_token():
    """Endpoint to get Spotify token"""
    try:
        token = SpotifyService.get_client_token()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_endpoint():
    return {"message": "Spotify API is working!"}