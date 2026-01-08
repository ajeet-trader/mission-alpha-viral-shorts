"""
Plugin loader - dynamically loads providers based on config.

This is the CORE of the modular architecture.
Change config → change provider → zero code changes!
"""

from importlib import import_module
from typing import Type, Dict, Any
from app.core.config import get_settings
from app.core.logger import log_step, log_success, log_error, show_provider_info
import logging

logger = logging.getLogger(__name__)


# ============================================
# PLUGIN REGISTRY
# Map provider names to their Python classes
# ============================================

PLUGIN_REGISTRY = {
    "content": {
        "reddit": "app.plugins.content.reddit_plugin.RedditProvider",
        "quotes": "app.plugins.content.quotes_plugin.QuotesProvider",
        "facts": "app.plugins.content.facts_plugin.FactsProvider",
    },
    "ai": {
        "langchain": "app.plugins.ai.langchain_plugin.LangChainProvider",
        "crewai": "app.plugins.ai.crewai_plugin.CrewAIProvider",
        "openai_direct": "app.plugins.ai.openai_plugin.OpenAIProvider",
        "groq": "app.plugins.ai.groq_plugin.GroqProvider",
        "huggingface": "app.plugins.ai.huggingface_plugin.HuggingFaceProvider",
    },
    "tts": {
        "gtts": "app.plugins.tts.gtts_plugin.GTTSProvider",
        "elevenlabs": "app.plugins.tts.elevenlabs_plugin.ElevenLabsProvider",
        "edge_tts": "app.plugins.tts.edge_tts_plugin.EdgeTTSProvider",
    },
    "video": {
        "moviepy": "app.plugins.video.moviepy_plugin.MoviePyProvider",
    },
    "upload": {
        "youtube": "app.plugins.upload.youtube_plugin.YouTubeProvider",
        "none": "app.plugins.upload.none_plugin.NoneProvider",
    },
    "database": {
        "supabase": "app.plugins.database.supabase_plugin.SupabaseProvider",
        "sqlite": "app.plugins.database.sqlite_plugin.SQLiteProvider",
    },
}


class PluginLoader:
    """
    Dynamically loads plugins based on configuration.
    
    This is the magic that enables zero-coupling architecture!
    """
    
    _cache: Dict[str, Any] = {}  # Cache loaded plugins
    
    @classmethod
    def load(cls, plugin_type: str, force_reload: bool = False) -> Any:
        """
        Load a plugin based on config with fallback support.
        
        Args:
            plugin_type: Type of plugin (ai, tts, video, etc.)
            force_reload: Force reload even if cached
            
        Returns:
            Instantiated plugin object
        """
        # Check cache
        if plugin_type in cls._cache and not force_reload:
            logger.debug(f"Using cached {plugin_type} plugin")
            return cls._cache[plugin_type]
        
        log_step(f"Loading {plugin_type.upper()} plugin")
        
        # Get settings
        settings = get_settings()
        provider_config = getattr(settings, plugin_type)
        primary_provider = provider_config.provider
        
        # Build provider list: primary + fallbacks
        providers_to_try = [primary_provider]
        
        # Add fallbacks if available
        if hasattr(provider_config, 'fallback'):
            fallback_list = provider_config.fallback
            if isinstance(fallback_list, list):
                # Filter out primary to avoid duplicate
                fallbacks = [p for p in fallback_list if p != primary_provider]
                providers_to_try.extend(fallbacks)
            elif isinstance(fallback_list, str) and fallback_list:
                if fallback_list != primary_provider:
                    providers_to_try.append(fallback_list)
        
        last_error = None
        
        # Try each provider in order
        for provider_name in providers_to_try:
            try:
                logger.info(f"Attempting to load {plugin_type} provider: {provider_name}")
                
                # Get plugin class path from registry
                if plugin_type not in PLUGIN_REGISTRY:
                    raise ValueError(f"Unknown plugin type: {plugin_type}")
                
                if provider_name not in PLUGIN_REGISTRY[plugin_type]:
                    logger.warning(
                        f"Unknown {plugin_type} provider: {provider_name}. "
                        f"Available: {list(PLUGIN_REGISTRY[plugin_type].keys())}"
                    )
                    continue  # Try next fallback
                
                class_path = PLUGIN_REGISTRY[plugin_type][provider_name]
                
                # Dynamic import
                module_path, class_name = class_path.rsplit(".", 1)
                log_step(f"Importing {class_name} from {module_path}")
                
                module = import_module(module_path)
                plugin_class = getattr(module, class_name)
                
                # Instantiate with config
                plugin_instance = plugin_class(provider_config)
                
                # Cache
                cls._cache[plugin_type] = plugin_instance
                
                # Show which provider is active
                show_provider_info(plugin_type, provider_name)
                
                # Show if using fallback
                if provider_name != primary_provider:
                    logger.warning(f"⚠️  Using fallback provider: {provider_name} (primary '{primary_provider}' failed)")
                    log_success(f"{plugin_type.upper()} plugin loaded: {provider_name} (FALLBACK)")
                else:
                    log_success(f"{plugin_type.upper()} plugin loaded: {provider_name}")
                
                return plugin_instance
                
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to load {plugin_type} provider '{provider_name}': {str(e)}")
                # Continue to next fallback
                continue
        
        # All providers failed
        error_msg = (
            f"Failed to load {plugin_type} plugin. "
            f"Tried providers: {providers_to_try}. "
            f"Last error: {str(last_error)}"
        )
        log_error(error_msg)
        raise RuntimeError(error_msg)
    
    @classmethod
    def load_specific(cls, plugin_type: str, provider_name: str) -> Any:
        """
        Load a specific provider (override config).
        
        Useful for manual testing/comparison.
        """
        if plugin_type not in PLUGIN_REGISTRY:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
        
        if provider_name not in PLUGIN_REGISTRY[plugin_type]:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        class_path = PLUGIN_REGISTRY[plugin_type][provider_name]
        module_path, class_name = class_path.rsplit(".", 1)
        
        module = import_module(module_path)
        plugin_class = getattr(module, class_name)
        
        # Get config for this type
        settings = get_settings()
        config = getattr(settings, plugin_type)
        
        return plugin_class(config)
    
    @classmethod
    def clear_cache(cls):
        """Clear plugin cache (useful for hot-reloading)."""
        cls._cache.clear()
        log_success("Plugin cache cleared")
    
    @classmethod
    def get_available_providers(cls, plugin_type: str) -> list:
        """Get list of available providers for a plugin type."""
        return list(PLUGIN_REGISTRY.get(plugin_type, {}).keys())
