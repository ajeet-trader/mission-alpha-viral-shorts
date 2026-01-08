"""
Groq AI Provider

Super fast inference using Groq's LPU hardware.
FREE tier: 30 req/min, 6000 req/day
"""

import os
import logging
from typing import Optional
from app.core.interfaces import IAIProvider, ContentItem, ScriptResult
from app.core.logger import log_step, log_success, step_progress, console

logger = logging.getLogger(__name__)


class GroqProvider(IAIProvider):
    """Groq AI provider - extremely fast inference."""
    
    def __init__(self, config):
        self.config = config
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = "llama-3.3-70b-versatile"  # Current model (Dec 2024)
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        # Initialize Groq client
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            log_success(f"Groq initialized with {self.model}")
        except ImportError:
            raise ImportError("Please install groq: pip install groq")
    
    async def generate_script(self, content: ContentItem) -> ScriptResult:
        """Generate Hinglish script using Groq."""
        log_step("Generating script with Groq", f"Model: {self.model}")
        
        prompt = f"""You are a viral short-form content creator for Indian audience.
Create a script in HINGLISH (Hindi + English mix) based on:

Content: {content.title}
Details: {content.body[:500] if content.body else ''}

Create:
1. HOOK (first 3 seconds) - attention grabber
2. BODY (main content) - value delivery  
3. CTA (call to action) - engagement prompt

Keep it under 60 seconds when spoken. Be energetic and relatable!"""
        
        with step_progress("Calling Groq API..."):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
        
        raw_response = response.choices[0].message.content
        
        # Parse sections - extract clean content without labels
        hook = self._extract_section(raw_response, "HOOK", "BODY")
        body = self._extract_section(raw_response, "BODY", "CTA")
        cta = self._extract_section(raw_response, "CTA", None)
        
        # Fallback values
        hook = hook or raw_response[:100]
        body = body or raw_response
        cta = cta or "Like aur share karo!"
        
        # Build clean full_script from extracted sections (no labels)
        full_script = f"{hook}\n\n{body}\n\n{cta}"
        
        log_success(f"✓ Script generated with Groq ({len(full_script)} chars)")
        
        return ScriptResult(
            hook=hook,
            body=body,
            cta=cta,
            full_script=full_script,
            provider="groq",
            metadata={"model": self.model}
        )
    
    def _extract_section(self, text: str, start: str, end: Optional[str]) -> str:
        """Extract section from script."""
        try:
            start_idx = text.upper().find(start)
            if start_idx == -1:
                return ""
            
            start_idx = text.find("\n", start_idx) + 1
            
            if end:
                end_idx = text.upper().find(end)
                if end_idx == -1:
                    return text[start_idx:].strip()
                return text[start_idx:end_idx].strip()
            
            return text[start_idx:].strip()
        except:
            return ""
    
    def get_provider_name(self) -> str:
        return f"Groq ({self.model})"
