"""Main API router that combines all endpoints."""
from fastapi import APIRouter

from app.api.endpoints import matching, health
from app.core.config import settings

# Create the main API router
api_router = APIRouter(prefix=settings.API_V1_STR)

# Add routes from endpoint modules
api_router.include_router(matching.router, tags=["matching"])
api_router.include_router(health.router, tags=["health"]) 