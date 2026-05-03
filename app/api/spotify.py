from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional
import requests
from app.services.spotify_service import SpotifyService
from app.core.security import verify_token
from app.api.auth import user_sessions

router = APIRouter()

VALID_TIME_RANGES = {"short_term", "medium_term", "long_term"}

def get_authenticated_session(token: Dict = Depends(verify_token)) -> Dict:
    """Resolve the in-memory Spotify session for the current JWT."""
    user_id = token.get("sub")
    session = user_sessions.get(user_id)

    if not session or not session.get("access_token"):
        raise HTTPException(
            status_code=401,
            detail="User not found or session expired"
        )

    return session

@router.get("/token")
async def get_token():
    """Check that a Spotify client credentials token can be obtained."""
    try:
        token = SpotifyService.get_client_token()
        token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else "***"
        return {
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

@router.get("/me/profile")
async def get_my_profile(
    session: Dict = Depends(get_authenticated_session)
):
    """Get the logged-in user's Spotify profile."""
    try:
        return {"profile": SpotifyService.get_user_profile(session["access_token"])}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/me/top/tracks")
async def get_my_top_tracks(
    time_range: str = Query("medium_term", description="short_term, medium_term, or long_term"),
    limit: int = Query(10, ge=1, le=50, description="Number of results (1-50)"),
    session: Dict = Depends(get_authenticated_session)
):
    """Get the logged-in user's top tracks."""
    if time_range not in VALID_TIME_RANGES:
        raise HTTPException(
            status_code=422,
            detail="time_range must be short_term, medium_term, or long_term"
        )

    try:
        tracks = SpotifyService.get_user_top_tracks(
            access_token=session["access_token"],
            time_range=time_range,
            limit=limit
        )
        return {"time_range": time_range, "limit": limit, "tracks": tracks}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/me/top/artists")
async def get_my_top_artists(
    time_range: str = Query("medium_term", description="short_term, medium_term, or long_term"),
    limit: int = Query(10, ge=1, le=50, description="Number of results (1-50)"),
    session: Dict = Depends(get_authenticated_session)
):
    """Get the logged-in user's top artists."""
    if time_range not in VALID_TIME_RANGES:
        raise HTTPException(
            status_code=422,
            detail="time_range must be short_term, medium_term, or long_term"
        )

    try:
        artists = SpotifyService.get_user_top_artists(
            access_token=session["access_token"],
            time_range=time_range,
            limit=limit
        )
        return {"time_range": time_range, "limit": limit, "artists": artists}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/me/recently-played")
async def get_my_recently_played(
    limit: int = Query(10, ge=1, le=50, description="Number of results (1-50)"),
    session: Dict = Depends(get_authenticated_session)
):
    """Get the logged-in user's recently played tracks."""
    try:
        items = SpotifyService.get_recently_played(
            access_token=session["access_token"],
            limit=limit
        )
        return {"limit": limit, "items": items}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
