"""
LangChain AI Provider Plugin

Uses Google GenAI directly for script generation.
"""

from google import genai
from typing import Dict
import os
from app.core.interfaces import IAIProvider, ContentItem, ScriptResult
from app.core.logger import log_step, log_success, step_progress
import logging

logger = logging.getLogger(__name__)


class LangChainProvider(IAIProvider):
    """Google GenAI-based script generator with multi-step generation."""
    
    def __init__(self, config):
        self.config = config
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        self.client = genai.Client(api_key=api_key)
        self.model = config.model
        
        log_success(f"Google GenAI initialized with {config.model}")
    
    async def generate_script(self, content: ContentItem, style: str = "hinglish") -> ScriptResult:
        """Generate script using multi-step prompts."""
        log_step("Generating script with Google GenAI", f"Content: {content.title[:50]}...")
        
        with step_progress("🔗 Creating hook..."):
            hook = await self._generate_hook(content)
        
        with step_progress("🔗 Writing body..."):
            body = await self._generate_body(content, hook)
        
        with step_progress("🔗 Adding CTA..."):
            cta = await self._generate_cta(content.type)
        
        full_script = f"{hook}\n\n{body}\n\n{cta}"
        
        log_success("✓ Script generated with Google GenAI")
        
        return ScriptResult(
            hook=hook,
            body=body,
            cta=cta,
            full_script=full_script,
            provider="google_genai",
            metadata={
                "model": self.config.model,
                "temperature": self.config.temperature,
                "content_type": content.type
            }
        )
    
    async def _generate_hook(self, content: ContentItem) -> str:
        """Generate attention-grabbing hook."""
        prompt_text = f"""
Create a 10-15 second attention-grabbing hook in Hinglish for a YouTube Short.

Content: {content.title}
Details: {content.body[:200]}

Rules:
- Start with a question or shocking statement
- Mix Hindi and English naturally
- Keep it under 25 words
- Create curiosity

Hook:
"""
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt_text
        )
        return response.text.strip()
    
    async def _generate_body(self, content: ContentItem, hook: str) -> str:
        """Generate main body."""
        prompt_text = f"""
Expand this hook into a 30-35 second engaging script in Hinglish.

Hook: {hook}
Content: {content.body[:300]}
Type: {content.type}

Rules:
- Continue from the hook naturally
- Keep it conversational (Hinglish)
- Tell the story/fact clearly
- Build up to a conclusion
- Total should be about 40-45 seconds when spoken

Body:
"""
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt_text
        )
        return response.text.strip()
    
    async def _generate_cta(self, content_type: str) -> str:
        """Generate call-to-action."""
        ctas = {
            "story": "Agar yeh story pasand aayi toh like karo aur comment mein batao!",
            "quote": "Is quote se inspired ho? Like aur share karo apne dosto ke saath!",
            "fact": "Aur interesting facts ke liye follow karo! Like aur subscribe bhi karna!"
        }
        return ctas.get(content_type, "Like karo aur follow karo more content ke liye!")
    
    def get_provider_name(self) -> str:
        return f"Google GenAI ({self.model})"
