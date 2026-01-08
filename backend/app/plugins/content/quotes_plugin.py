"""
Quotes Content Provider Plugin

Fetches motivational quotes from multiple free APIs with curated Hinglish fallback.
"""

import requests
from typing import List
from datetime import datetime
from app.core.interfaces import IContentProvider, ContentItem
from app.core.logger import log_step, log_success, log_warning
import logging
import random

logger = logging.getLogger(__name__)


# Curated Hinglish quotes for Indian audience
HINGLISH_QUOTES = [
    "Sapne woh nahi jo neend mein aaye, sapne woh hain jo neend ude de.",
    "Koshish karne walon ki kabhi haar nahi hoti.",
    "Haar kar jeetne wale ko hi baazigar kehte hain.",
    "Mushkil waqt mein sabse bada support aapka hausla hai.",
    "Success ka shortcut sirf hardwork hai.",
    "Apni galtiyon se seekho aur aage badho.",
    "Confidence aur patience success ki key hain.",
    "Apne goals par focus karo, baaki sab automatically hoga.",
    "Life mein risk lena zaroori hai, tabhi aage badhoge.",
    "Positive soch rakhoge toh zindagi asaan ho jayegi."
]


class QuotesProvider(IContentProvider):
    """Quotes fetcher from multiple APIs with Hinglish fallback."""
    
    def __init__(self, config):
        self.config = config
        self.apis = [
            "https://api.quotable.io/random",
            "https://zenquotes.io/api/random",
        ]
    
    async def fetch_content(self, limit: int = 10) -> List[ContentItem]:
        """Fetch motivational quotes."""
        log_step("Fetching quotes", 
                f"Categories: {', '.join(self.config.quotes.categories)}")
        
        items = []
        
        # Try APIs first
        for api_url in self.apis:
            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        data = data[0]
                    
                    quote_text = data.get('content') or data.get('q') or data.get('quote', '')
                    author = data.get('author') or data.get('a') or "Unknown"
                    
                    if quote_text:
                        item = ContentItem(
                            id=f"quote_{hash(quote_text)}",
                            type="quote",
                            title=f"{quote_text[:50]}...",
                            body=quote_text,
                            source=f"Quote by {author}",
                            score=await self.score_virality(quote_text),
                            created_at=datetime.now()
                        )
                        items.append(item)
                        
                        if len(items) >= limit:
                            break
            except Exception as e:
                logger.warning(f"API {api_url} failed: {e}")
        
        # Fallback to curated Hinglish quotes
        if len(items) < limit:
            log_warning("Using curated Hinglish quotes")
            needed = limit - len(items)
            selected = random.sample(HINGLISH_QUOTES, min(needed, len(HINGLISH_QUOTES)))
            
            for quote in selected:
                item = ContentItem(
                    id=f"hinglish_{hash(quote)}",
                    type="quote",
                    title=quote[:50],
                    body=quote,
                    source="Curated Hinglish",
                    score=75.0,  # High score for curated content
                    created_at=datetime.now()
                )
                items.append(item)
        
        log_success(f"Fetched {len(items)} quotes")
        return items[:limit]
    
    async def score_virality(self, quote: str) -> float:
        """Score quote virality based on length and keywords."""
        score = 60  # Base score
        
        # Shorter quotes are more shareable
        if len(quote) < 100:
            score += 20
        elif len(quote) < 150:
            score += 10
        
        # Powerful keywords boost score
        power_words = ['success', 'dream', 'life', 'love', 'change', 'believe', 
                      'sapne', 'koshish', 'jeet']
        for word in power_words:
            if word.lower() in quote.lower():
                score += 5
        
        return min(score, 100)
