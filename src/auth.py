"""
Authentication utilities for NewsTrader API.
Implements API key-based authentication for securing endpoints.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from src.config import settings


# Define API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key from request header.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Include 'X-API-Key' header in your request.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key. Access denied.",
        )

    return api_key


def get_api_key_info() -> dict:
    """
    Get information about API key authentication.

    Returns:
        Dict with authentication information
    """
    return {
        "authentication": "API Key",
        "header_name": "X-API-Key",
        "description": "Include your API key in the 'X-API-Key' header for all requests",
        "example": "curl -H 'X-API-Key: your-api-key-here' http://localhost:8000/signals"
    }
