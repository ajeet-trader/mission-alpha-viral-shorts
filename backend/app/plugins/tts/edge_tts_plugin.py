"""
Edge TTS Provider

Microsoft Edge Text-to-Speech - FREE, unlimited, natural voices.
Much better quality than gTTS!
"""

import os
import logging
import asyncio
import uuid
from pathlib import Path
from typing import Optional
from app.core.interfaces import ITTSProvider, MediaFile
from app.core.logger import log_step, log_success, step_progress

logger = logging.getLogger(__name__)


class EdgeTTSProvider(ITTSProvider):
    """Microsoft Edge TTS - natural voices, FREE unlimited."""
    
    # Best Hindi voices
    VOICES = {
        "hi": "hi-IN-SwaraNeural",      # Female - natural
        "hi-male": "hi-IN-MadhurNeural", # Male - natural
        "en": "en-US-JennyNeural",       # English female
        "en-male": "en-US-GuyNeural",    # English male
        "hinglish": "hi-IN-SwaraNeural"  # For Hinglish content
    }
    
    def __init__(self, config):
        self.config = config
        self.language = getattr(config, 'language', 'hi')
        self.voice = self.VOICES.get(self.language, self.VOICES["hi"])
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        log_success(f"Edge TTS initialized with voice: {self.voice}")
    
    async def text_to_speech(
        self, 
        text: str, 
        output_path: Optional[str] = None
    ) -> MediaFile:
        """Convert text to natural speech using Edge TTS."""
        log_step("🎙️ Generating audio with Edge TTS", f"Voice: {self.voice}")
        
        try:
            import edge_tts
        except ImportError:
            raise ImportError("Please install edge-tts: pip install edge-tts")
        
        # Generate unique filename if not provided
        if not output_path:
            file_id = uuid.uuid4().hex[:8]
            output_path = str(self.output_dir / f"edge_{file_id}.mp3")
        
        with step_progress("Generating natural voice..."):
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
        
        # Get audio duration
        duration = await self._get_duration(output_path)
        
        log_success(f"✓ Audio generated: {duration:.1f}s (Edge TTS)")
        
        return MediaFile(
            path=output_path,
            duration=duration,
            provider="edge_tts",
            metadata={"voice": self.voice, "language": self.language}
        )
    
    async def _get_duration(self, path: str) -> float:
        """Get audio duration using mutagen or moviepy."""
        try:
            from mutagen.mp3 import MP3
            audio = MP3(path)
            return audio.info.length
        except:
            try:
                from moviepy.editor import AudioFileClip
                with AudioFileClip(path) as clip:
                    return clip.duration
            except:
                return 0.0
    
    def get_provider_name(self) -> str:
        return f"Edge TTS ({self.voice})"
    
    @classmethod
    def get_available_voices(cls) -> dict:
        """Return available voices."""
        return cls.VOICES
