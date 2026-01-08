"""
Content Router

Endpoints for fetching content from various providers.
"""

from fastapi import APIRouter, Depends
from typing import List
from app.core.interfaces import IContentProvider, ContentItem
from app.core.plugin_loader import PluginLoader

router = APIRouter()


def get_content_provider() -> IContentProvider:
    """Dependency: Load content provider from config."""
    return PluginLoader.load("content")


@router.get("/fetch", response_model=List[dict])
async def fetch_content(
    limit: int = 10,
    provider: IContentProvider = Depends(get_content_provider)
):
    """
    Fetch content from configured provider.
    
    The provider is determined by config.yaml.
    Change content.provider to switch sources!
    """
    items = await provider.fetch_content(limit=limit)
    
    return [
        {
            "id": item.id,
            "type": item.type,
            "title": item.title,
            "body": item.body[:200],  # Truncate for API response
            "source": item.source,
            "score": item.score
        }
        for item in items
    ]


@router.get("/providers")
async def list_providers():
    """List available content providers."""
    available = PluginLoader.get_available_providers("content")
    return {
        "providers": available,
        "current": PluginLoader.load("content").config.provider
    }
