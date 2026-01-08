"""
AI Provider Wrapper with Runtime Fallback

This wrapper catches API errors and automatically switches to fallback providers.
Works at the method call level, not just plugin loading.
"""

import logging
from typing import Any, List, Optional
from app.core.plugin_loader import PluginLoader
from app.core.config import get_settings
from app.core.logger import log_step, log_success, log_error, console

logger = logging.getLogger(__name__)


class AIProviderWithFallback:
    """
    Wraps AI provider with automatic fallback on errors.
    
    Usage:
        ai = AIProviderWithFallback()
        script = await ai.generate_script(content)  # Auto-fallback on error
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.primary_provider_name = self.settings.ai.provider
        self.fallback_providers = getattr(self.settings.ai, 'fallback', [])
        
        # Build ordered list of providers to try
        self.providers_to_try = [self.primary_provider_name]
        if isinstance(self.fallback_providers, list):
            self.providers_to_try.extend([
                p for p in self.fallback_providers 
                if p != self.primary_provider_name
            ])
        elif self.fallback_providers:
            if self.fallback_providers != self.primary_provider_name:
                self.providers_to_try.append(self.fallback_providers)
        
        self._current_provider = None
        self._current_provider_name = None
        self._load_primary()
    
    def _load_primary(self):
        """Load the primary provider."""
        try:
            self._current_provider = PluginLoader.load('ai')
            self._current_provider_name = self.primary_provider_name
        except Exception as e:
            logger.warning(f"Failed to load primary AI provider: {e}")
            self._current_provider = None
    
    def _load_fallback(self, provider_name: str):
        """Load a specific fallback provider."""
        try:
            # Clear cache to force reload with new provider
            PluginLoader._cache.pop('ai', None)
            
            # Temporarily override provider in config
            original_provider = self.settings.ai.provider
            self.settings.ai.provider = provider_name
            
            provider = PluginLoader.load('ai', force_reload=True)
            
            # Restore original
            self.settings.ai.provider = original_provider
            
            self._current_provider = provider
            self._current_provider_name = provider_name
            
            console.print(f"[yellow]⚠️  Switched to fallback AI: {provider_name}[/yellow]")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load fallback provider {provider_name}: {e}")
            return False
    
    async def generate_script(self, content: Any) -> Any:
        """
        Generate script with automatic fallback on errors.
        
        Tries each provider in order until one succeeds.
        """
        last_error = None
        tried_providers = []
        
        for provider_name in self.providers_to_try:
            try:
                # Load provider if needed
                if self._current_provider_name != provider_name:
                    if provider_name == self.primary_provider_name:
                        self._load_primary()
                    else:
                        if not self._load_fallback(provider_name):
                            continue
                
                if self._current_provider is None:
                    continue
                
                tried_providers.append(provider_name)
                
                # Try to generate
                log_step(f"🤖 Generating script with {provider_name}")
                result = await self._current_provider.generate_script(content)
                
                # Success!
                if provider_name != self.primary_provider_name:
                    log_success(f"✓ Script generated with {provider_name} (FALLBACK)")
                else:
                    log_success(f"✓ Script generated with {provider_name}")
                
                return result
                
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Check if it's a quota/rate limit error
                is_quota_error = any(x in error_msg for x in [
                    'quota', 'rate limit', '429', 'too many requests',
                    'resource_exhausted', 'exceeded'
                ])
                
                if is_quota_error:
                    console.print(f"[yellow]⚠️  {provider_name} quota exceeded, trying fallback...[/yellow]")
                else:
                    logger.warning(f"Error with {provider_name}: {e}")
                
                # Continue to next provider
                continue
        
        # All providers failed
        error_msg = (
            f"All AI providers failed. Tried: {tried_providers}. "
            f"Last error: {last_error}"
        )
        log_error(error_msg)
        raise RuntimeError(error_msg)
    
    @property
    def current_provider_name(self) -> str:
        """Get currently active provider name."""
        return self._current_provider_name or "none"


# Singleton instance for easy access
_ai_with_fallback: Optional[AIProviderWithFallback] = None


def get_ai_provider() -> AIProviderWithFallback:
    """Get AI provider with fallback support."""
    global _ai_with_fallback
    if _ai_with_fallback is None:
        _ai_with_fallback = AIProviderWithFallback()
    return _ai_with_fallback


def reset_ai_provider():
    """Reset the singleton (useful for testing)."""
    global _ai_with_fallback
    _ai_with_fallback = None
