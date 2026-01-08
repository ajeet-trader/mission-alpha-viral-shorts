"""
Core interfaces for all providers.

Each provider type has an abstract base class that defines
the contract all implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


# ============================================
# Data Models
# ============================================

@dataclass
class ContentItem:
    """Standardized content structure."""
    id: str
    type: str  # story, quote, fact
    title: str
    body: str
    source: str
    score: float  # Virality score
    created_at: datetime


@dataclass
class ScriptResult:
    """AI-generated script result."""
    hook: str
    body: str
    cta: str
    full_script: str
    provider: str  # Which AI provider generated this
    metadata: Dict


@dataclass
class MediaFile:
    """Generated media file info."""
    path: str
    duration: float
    provider: str
    metadata: Dict


# ============================================
# Provider Interfaces
# ============================================

class IContentProvider(ABC):
    """Interface for content scrapers."""
    
    @abstractmethod
    async def fetch_content(self, limit: int = 10) -> List[ContentItem]:
        """Fetch content items."""
        pass
    
    @abstractmethod
    async def score_virality(self, item: ContentItem) -> float:
        """Score content for viral potential (0-100)."""
        pass


class IAIProvider(ABC):
    """Interface for AI script generators."""
    
    @abstractmethod
    async def generate_script(
        self, 
        content: ContentItem,
        style: str = "hinglish"
    ) -> ScriptResult:
        """Generate script from content."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name for logging."""
        pass


class ITTSProvider(ABC):
    """Interface for Text-to-Speech providers."""
    
    @abstractmethod
    async def text_to_speech(
        self, 
        text: str,
        output_path: Optional[str] = None
    ) -> MediaFile:
        """Convert text to speech audio file."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name for logging."""
        pass


class IVideoProvider(ABC):
    """Interface for video assembly providers."""
    
    @abstractmethod
    async def assemble_video(
        self,
        audio_path: str,
        script: str,
        background_url: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> MediaFile:
        """Assemble final video with audio, background, and captions."""
        pass


class IUploadProvider(ABC):
    """Interface for upload providers."""
    
    @abstractmethod
    async def upload(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict:
        """Upload video to platform."""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name."""
        pass


class IDatabaseProvider(ABC):
    """Interface for database providers."""
    
    @abstractmethod
    async def insert(self, table: str, data: Dict) -> str:
        """Insert data, return ID."""
        pass
    
    @abstractmethod
    async def query(
        self, 
        table: str, 
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Query data with optional filters."""
        pass
    
    @abstractmethod
    async def update(
        self,
        table: str,
        id: str,
        data: Dict
    ) -> bool:
        """Update record by ID."""
        pass
