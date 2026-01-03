from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import RedirectResponse
from typing import Dict
import json

from app.services.auth_service import AuthService
from app.core.security import create_access_token, verify_token

router = APIRouter()

# Store sessions in memory (in production, use Redis or database)
user_sessions = {}

@router.get("/login")
async def spotify_login():
    """Redirect user to Spotify login page"""
    auth_url = AuthService.get_authorization_url()
    return RedirectResponse(auth_url)

@router.get("/callback")
async def spotify_callback(
    code: str = None,
    state: str = None,
    error: str = None
):
    """Handle Spotify OAuth callback"""
    
    # Check for errors from Spotify
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Spotify authorization error: {error}"
        )
    
    # Validate state for CSRF protection
    if not AuthService.validate_state(state):
        raise HTTPException(
            status_code=400,
            detail="Invalid state parameter"
        )
    
    if not code:
        raise HTTPException(
            status_code=400,
            detail="No authorization code provided"
        )
    
    try:
        # Exchange code for tokens
        token_data = AuthService.exchange_code_for_token(code)
        
        # Get user profile from Spotify
        user_profile = AuthService.get_user_profile(
            token_data["access_token"]
        )
        
        # Create our own JWT token
        user_data = {
            "spotify_id": user_profile["id"],
            "display_name": user_profile.get("display_name", ""),
            "email": user_profile.get("email", ""),
            "country": user_profile.get("country", ""),
            "profile_image": user_profile.get("images", [{}])[0].get("url", ""),
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", ""),
            "expires_in": token_data["expires_in"]
        }
        
        # Create JWT token for our app
        jwt_token = create_access_token(data={"sub": user_profile["id"]})
        
        # Store session (in production, use database)
        user_sessions[user_profile["id"]] = {
            **user_data,
            "jwt_token": jwt_token
        }
        
        # Redirect to frontend with token
        from fastapi.responses import RedirectResponse
        import json
        import base64
        
        # Prepare data for frontend
        frontend_data = {
            "success": True,
            "token": jwt_token,
            "user": {
                "spotify_id": user_profile["id"],
                "display_name": user_profile.get("display_name", ""),
                "email": user_profile.get("email", ""),
                "profile_image": user_profile.get("images", [{}])[0].get("url", "")
            }
        }
        
        # Encode data to pass in URL
        data_json = json.dumps(frontend_data)
        data_b64 = base64.b64encode(data_json.encode()).decode()
        
        # Redirect to frontend callback page
        frontend_url = f"http://localhost:3000/auth/callback?data={data_b64}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )



@router.get("/me")
async def get_current_user(
    token: str = Depends(verify_token)
):
    """Get current user data"""
    user_id = token.get("sub")
    
    if user_id not in user_sessions:
        raise HTTPException(
            status_code=401,
            detail="User not found or session expired"
        )
    
    user_data = user_sessions[user_id].copy()
    # Don't return sensitive tokens
    user_data.pop("access_token", None)
    user_data.pop("refresh_token", None)
    
    return {"user": user_data}

@router.get("/logout")
async def logout(
    token: str = Depends(verify_token)
):
    """Logout user and clear session"""
    user_id = token.get("sub")
    
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    return {"success": True, "message": "Logged out successfully"}
