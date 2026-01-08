"""
gTTS Provider Plugin

Free Google Text-to-Speech for Hindi voice synthesis.
"""

from gtts import gTTS
import os
from pathlib import Path
from app.core.interfaces import ITTSProvider, MediaFile
from app.core.logger import log_step, log_success
import logging
import hashlib

logger = logging.getLogger(__name__)


class GTTSProvider(ITTSProvider):
    """Google TTS provider for free Hindi voice."""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        log_success("gTTS provider initialized")
    
    async def text_to_speech(self, text: str, output_path: str = None) -> MediaFile:
        """Convert text to Hindi speech."""
        log_step("🎙️ Generating audio with gTTS", f"Language: {self.config.language}")
        
        # Clean text
        clean_text = text.replace('\n', ' ').strip()
        
        # Generate output path if not provided
        if not output_path:
            text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
            output_path = str(self.output_dir / f"tts_{text_hash}.mp3")
        
        # Generate speech
        tts = gTTS(
            text=clean_text,
            lang=self.config.language,
            slow=self.config.slow
        )
        
        tts.save(output_path)
        
        # Get duration (approximate: 150 words per minute for Hindi)
        word_count = len(clean_text.split())
        duration = (word_count / 150) * 60  # seconds
        
        log_success(f"✓ Audio generated: {duration:.1f}s")
        
        return MediaFile(
            path=output_path,
            duration=duration,
            provider="gtts",
            metadata={
                "language": self.config.language,
                "word_count": word_count
            }
        )
    
    def get_provider_name(self) -> str:
        return "gTTS (Google)"
