"""
ElevenLabs TTS Provider

High-quality voice synthesis using ElevenLabs API.
"""

from elevenlabs import generate, save
import os
from pathlib import Path
from app.core.interfaces import ITTSProvider, MediaFile
from app.core.logger import log_step, log_success
import hashlib


class ElevenLabsProvider(ITTSProvider):
    """ElevenLabs  TTS for premium voice quality."""
    
    def __init__(self, config):
        self.config = config
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found")
        
        log_success("ElevenLabs provider initialized")
    
    async def text_to_speech(self, text: str, output_path: str = None) -> MediaFile:
        """Convert text to speech using ElevenLabs."""
        log_step("🎙️ Generating audio with ElevenLabs", f"Voice: {self.config.elevenlabs.voice}")
        
        clean_text = text.replace('\n', ' ').strip()
        
        if not output_path:
            text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
            output_path = str(self.output_dir / f"elevenlabs_{text_hash}.mp3")
        
        # Generate audio
        audio = generate(
            text=clean_text,
            voice=self.config.elevenlabs.voice,
            model=self.config.elevenlabs.model,
            api_key=self.api_key
        )
        
        save(audio, output_path)
        
        # Estimate duration
        word_count = len(clean_text.split())
        duration = (word_count / 150) * 60
        
        log_success(f"✓ High-quality audio: {duration:.1f}s")
        
        return MediaFile(
            path=output_path,
            duration=duration,
            provider="elevenlabs",
            metadata={
                "voice": self.config.elevenlabs.voice,
                "model": self.config.elevenlabs.model
            }
        )
    
    def get_provider_name(self) -> str:
        return f"ElevenLabs ({self.config.elevenlabs.voice})"
