"""
Pexels Video Background Provider

Fetches engaging background videos from Pexels API.
FREE with API key.
"""

import os
import logging
import httpx
import random
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from app.core.logger import log_step, log_success, step_progress

# Ensure .env is loaded
load_dotenv()

logger = logging.getLogger(__name__)


class PexelsVideoProvider:
    """Fetches background videos from Pexels."""
    
    BASE_URL = "https://api.pexels.com/videos/search"
    
    # Video categories that work well for shorts
    CATEGORIES = [
        "satisfying",
        "nature",
        "abstract",
        "cooking",
        "city",
        "ocean",
        "clouds",
        "fire",
        "water",
        "technology"
    ]
    
    def __init__(self, cache_dir: str = "cache/backgrounds"):
        self.api_key = os.getenv("PEXELS_API_KEY")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.api_key:
            logger.warning("PEXELS_API_KEY not found - will use gradient backgrounds")
    
    async def fetch_video(
        self, 
        query: Optional[str] = None, 
        duration_min: int = 10,
        orientation: str = "portrait"
    ) -> Optional[str]:
        """
        Fetch a video from Pexels.
        
        Args:
            query: Search query (random category if None)
            duration_min: Minimum video duration in seconds
            orientation: portrait/landscape
            
        Returns:
            Path to downloaded video file, or None if failed
        """
        if not self.api_key:
            return None
        
        query = query or random.choice(self.CATEGORIES)
        log_step(f"🎬 Fetching Pexels video", f"Query: {query}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL,
                    headers={"Authorization": self.api_key},
                    params={
                        "query": query,
                        "orientation": orientation,
                        "size": "medium",
                        "per_page": 15
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
            
            videos = data.get("videos", [])
            if not videos:
                logger.warning(f"No videos found for query: {query}")
                return None
            
            # Filter by duration and pick random
            suitable = [
                v for v in videos 
                if v.get("duration", 0) >= duration_min
            ]
            
            if not suitable:
                suitable = videos  # Use any if none match duration
            
            video = random.choice(suitable)
            
            # Get the HD video file (prefer 720p for shorts)
            video_files = video.get("video_files", [])
            best_file = None
            
            for vf in video_files:
                height = vf.get("height", 0)
                if 720 <= height <= 1080:
                    best_file = vf
                    break
            
            if not best_file and video_files:
                best_file = video_files[0]
            
            if not best_file:
                logger.warning("No suitable video file found")
                return None
            
            # Download video
            video_url = best_file.get("link")
            video_id = video.get("id")
            cache_path = self.cache_dir / f"pexels_{video_id}.mp4"
            
            # Check cache
            if cache_path.exists():
                log_success(f"✓ Using cached video: {cache_path.name}")
                return str(cache_path)
            
            with step_progress(f"Downloading {best_file.get('width')}x{best_file.get('height')}..."):
                async with httpx.AsyncClient() as client:
                    video_response = await client.get(video_url, timeout=60.0)
                    video_response.raise_for_status()
                    
                    with open(cache_path, "wb") as f:
                        f.write(video_response.content)
            
            log_success(f"✓ Downloaded: {cache_path.name} ({video.get('duration')}s)")
            return str(cache_path)
            
        except Exception as e:
            logger.error(f"Pexels fetch failed: {e}")
            return None
    
    def clear_cache(self):
        """Clear cached videos."""
        for f in self.cache_dir.glob("*.mp4"):
            f.unlink()
        log_success("Cache cleared")


# Singleton
_pexels_provider: Optional[PexelsVideoProvider] = None


def get_pexels_provider() -> PexelsVideoProvider:
    global _pexels_provider
    if _pexels_provider is None:
        _pexels_provider = PexelsVideoProvider()
    return _pexels_provider
