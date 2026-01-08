"""
Configuration loader using Pydantic for type-safe settings.

Loads config.yaml and provides type-checked access to all settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, List, Optional
import yaml
from pathlib import Path


class RedditConfig(BaseSettings):
    model_config = {"extra": "allow"}
    subreddits: List[str] = ["india"]
    min_upvotes: int = 100
    limit: int = 10


class QuotesConfig(BaseSettings):
    categories: List[str] = ["motivational"]
    limit: int = 10


class ContentConfig(BaseSettings):
    provider: str = "reddit"
    fallback: str = "quotes"
    reddit: RedditConfig = RedditConfig()
    quotes: QuotesConfig = QuotesConfig()


class MultiAgentConfig(BaseSettings):
    enabled: bool = False
    agents: List[str] = ["researcher", "scriptwriter"]


class AIConfig(BaseSettings):
    provider: str = "langchain"
    model: str = "gemini-pro"
    temperature: float = 0.7
    multi_agent: MultiAgentConfig = MultiAgentConfig()
    fallback: List[str] = []


class ElevenLabsConfig(BaseSettings):
    voice: str = "Bella"
    model: str = "eleven_multilingual_v2"


class TTSConfig(BaseSettings):
    provider: str = "gtts"
    language: str = "hi"
    slow: bool = False
    elevenlabs: ElevenLabsConfig = ElevenLabsConfig()


class BackgroundConfig(BaseSettings):
    source: str = "pexels"
    categories: List[str] = ["satisfying", "nature"]
    cache_dir: str = "cache/backgrounds"


class CaptionsConfig(BaseSettings):
    enabled: bool = True
    style: str = "word_by_word"
    font: str = "Arial"
    font_size: int = 60
    color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: int = 2


class VideoConfig(BaseSettings):
    provider: str = "moviepy"
    resolution: str = "1080x1920"
    fps: int = 30
    background: BackgroundConfig = BackgroundConfig()
    captions: CaptionsConfig = CaptionsConfig()


class YouTubeConfig(BaseSettings):
    category: str = "22"
    privacy: str = "public"
    tags: List[str] = ["shorts", "viral"]


class UploadConfig(BaseSettings):
    provider: str = "youtube"
    youtube: YouTubeConfig = YouTubeConfig()


class SupabaseConfig(BaseSettings):
    url: Optional[str] = None
    key: Optional[str] = None


class SQLiteConfig(BaseSettings):
    db_path: str = "data/factory.db"


class DatabaseConfig(BaseSettings):
    provider: str = "sqlite"
    supabase: SupabaseConfig = SupabaseConfig()
    sqlite: SQLiteConfig = SQLiteConfig()


class LoggingConfig(BaseSettings):
    level: str = "INFO"
    show_progress: bool = True
    colorize: bool = True
    log_file: str = "logs/factory.log"


class AppConfig(BaseSettings):
    name: str = "Mission Alpha"
    version: str = "2.0"
    debug: bool = True


class OutputConfig(BaseSettings):
    base_dir: str = "output"
    audio_dir: str = "output/audio"
    video_dir: str = "output/videos"
    temp_dir: str = "output/temp"


class Settings(BaseSettings):
    """Main settings object."""
    model_config = {"extra": "allow"}
    app: AppConfig = AppConfig()
    logging: LoggingConfig = LoggingConfig()
    content: ContentConfig = ContentConfig()
    ai: AIConfig = AIConfig()
    tts: TTSConfig = TTSConfig()
    video: VideoConfig = VideoConfig()
    upload: UploadConfig = UploadConfig()
    database: DatabaseConfig = DatabaseConfig()
    output: OutputConfig = OutputConfig()


# Global settings instance
_settings: Optional[Settings] = None


def load_config(config_path: str = "config.yaml") -> Settings:
    """Load configuration from YAML file."""
    global _settings
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Use defaults
        _settings = Settings()
        return _settings
    
    # Load YAML
    with open(config_file, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    
    # Parse with Pydantic
    _settings = Settings(**config_dict)
    return _settings


def get_settings() -> Settings:
    """Get current settings (load if not loaded)."""
    global _settings
    
    if _settings is None:
        _settings = load_config()
    
    return _settings


def reload_config() -> Settings:
    """Reload configuration from file."""
    global _settings
    _settings = None
    return load_config()
