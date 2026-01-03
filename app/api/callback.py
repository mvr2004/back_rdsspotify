from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import urllib.parse

router = APIRouter()

@router.get("/callback")
async def spotify_callback_redirect(request: Request):
    """Redirect Spotify callback to our API endpoint"""
    
    # Get all query parameters
    query_params = dict(request.query_params)
    
    # Build new URL with /api/auth/callback
    base_url = "http://localhost:8000/api/auth/callback"
    
    if query_params:
        query_string = urllib.parse.urlencode(query_params)
        redirect_url = f"{base_url}?{query_string}"
    else:
        redirect_url = base_url
    
    return RedirectResponse(url=redirect_url)