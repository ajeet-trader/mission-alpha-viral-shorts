"""OpenAI Direct Provider - Direct API calls."""

import openai
import os
from app.core.interfaces import IAIProvider, ContentItem, ScriptResult
from app.core.logger import log_step, log_success


class OpenAIProvider(IAIProvider):
    """Direct OpenAI API for script generation."""
    
    def __init__(self, config):
        self.config = config
        openai.api_key = os.getenv('OPENAI_API_KEY')
        log_success("OpenAI Direct initialized")
    
    async def generate_script(self, content: ContentItem, style: str = "hinglish") -> ScriptResult:
        """Generate script using OpenAI ChatGPT."""
        log_step("Generating with OpenAI GPT-4")
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Hinglish scriptwriter for viral YouTube Shorts targeting Indian audience."},
                {"role": "user", "content": f"Write a 45-second viral script about: {content.title}\n\n{content.body}"}
            ],
            temperature=self.config.temperature
        )
        
        script = response.choices[0].message.content
        
        return ScriptResult(
            hook=script[:100],
            body=script[100:-100],
            cta=script[-100:],
            full_script=script,
            provider="openai_direct",
            metadata={"model": "gpt-4"}
        )
    
    def get_provider_name(self) -> str:
        return "OpenAI GPT-4"
