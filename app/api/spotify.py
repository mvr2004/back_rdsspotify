from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import requests
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

@router.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    type: str = Query("track", description="Type of search (track, artist, album, playlist)"),
    limit: int = Query(20, ge=1, le=50, description="Number of results (1-50)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    market: Optional[str] = Query(None, description="Market code (e.g., PT, US)")
):
    """Search for items on Spotify"""
    try:
        results = SpotifyService.search(
            query=q,
            search_type=type,
            limit=limit,
            offset=offset,
            market=market
        )
        
        # Get total results
        total = 0
        if type == "track":
            total = results.get("tracks", {}).get("total", 0)
        elif type == "artist":
            total = results.get("artists", {}).get("total", 0)
        elif type == "album":
            total = results.get("albums", {}).get("total", 0)
        elif type == "playlist":
            total = results.get("playlists", {}).get("total", 0)
        
        return {
            "query": q,
            "type": type,
            "limit": limit,
            "offset": offset,
            "total": total,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/tracks")
async def search_tracks(
    q: str = Query(..., description="Search query for tracks"),
    limit: int = Query(20, ge=1, le=50, description="Number of results (1-50)"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Search for tracks with formatted results"""
    try:
        tracks = SpotifyService.search_tracks(
            query=q,
            limit=limit,
            offset=offset
        )
        
        return {
            "query": q,
            "limit": limit,
            "offset": offset,
            "total_tracks": len(tracks),
            "tracks": tracks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Spotify API is working!"}


@router.get("/search/artists")
async def search_artists(
    q: str = Query(..., description="Search query for artists"),
    limit: int = Query(20, ge=1, le=50, description="Number of results (1-50)"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Search for artists with formatted results"""
    try:
        artists = SpotifyService.search_artists(
            query=q,
            limit=limit,
            offset=offset
        )
        
        return {
            "query": q,
            "limit": limit,
            "offset": offset,
            "total_artists": len(artists),
            "artists": artists
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))