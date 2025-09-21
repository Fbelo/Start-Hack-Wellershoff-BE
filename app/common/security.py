import os
from fastapi import HTTPException, Request, status
from fastapi.security import APIKeyHeader
from typing import Optional

# Read API key from environment variable
FRONTEND_API_KEY = os.getenv("FRONTEND_API_KEY")
if not FRONTEND_API_KEY:
    raise ValueError("FRONTEND_API_KEY environment variable is not set")

# Define header name for the API key
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(request: Request) -> None:
    """
    Middleware function to verify the API key in request headers.
    Raises an HTTPException if the key is missing or invalid.
    """
    # Skip API key verification for certain paths if needed
    # For example, you might want to skip for docs or redoc
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return
    
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "API key required"},
        )
    
    if api_key != FRONTEND_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Invalid API key"},
        )

def get_api_key(api_key_header: str = API_KEY_HEADER) -> str:
    """
    Dependency function for FastAPI routes that need API key validation.
    Can be used with Depends() in route definitions for specific endpoints.
    """
    if api_key_header != FRONTEND_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Invalid API key"},
        )
    return api_key_header