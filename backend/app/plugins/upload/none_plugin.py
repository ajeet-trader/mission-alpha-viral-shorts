"""
None Upload Provider - for testing without uploading.
"""

from typing import Dict, List
from app.core.interfaces import IUploadProvider
from app.core.logger import log_step, log_info


class NoneProvider(IUploadProvider):
    """No-op upload provider for testing."""
    
    def __init__(self, config):
        self.config = config
        log_info("Upload disabled (none provider)")
    
    async def upload(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict:
        """Mock upload."""
        log_step("📤 Skipping upload (provider=none)")
        
        return {
            "id": f"local_{hash(title)}",
            "url": video_path,
            "status": "skipped"
        }
    
    def get_platform_name(self) -> str:
        return "None (Local Only)"
