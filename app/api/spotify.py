import requests
from fastapi import APIRouter, HTTPException
from app.services.spotify_service import SpotifyService

router = APIRouter()

@router.get("/token")
async def get_token():
    """Get Spotify access token"""
    try:
        token = SpotifyService.get_client_token()
        # Return only first and last few chars for security
        token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else "***"
        return {
            "token": token,
            "token_preview": token_preview,
            "message": "Token obtained successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/token/health")
async def check_token_health():
    """Check if Spotify token is working"""
    try:
        token = SpotifyService.get_client_token()
        
        # Test the token with a simple API call
        test_response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": "test", "type": "track", "limit": 1}
        )
        
        return {
            "status": "healthy",
            "token_valid": test_response.status_code == 200,
            "spotify_api_status": test_response.status_code,
            "message": "Token is working correctly"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Spotify API is working!"}