"""
Facts Content Provider Plugin

Fetches interesting facts with curated Indian facts fallback.
"""

import requests
from typing import List
from datetime import datetime
from app.core.interfaces import IContentProvider, ContentItem
from app.core.logger import log_step, log_success
import logging
import random

logger = logging.getLogger(__name__)


# Curated facts for Indian audience
INDIAN_FACTS = [
    "India hai duniya ka sabse bada democracy! 1.4 billion log voting karte hain.",
    "Shampoo ka invention India mein hua tha. Hinglish word 'champo' se aaya.",
    "Chess game ki shuruaat India mein hui thi, 6th century mein.",
    "Yoga ki origin India mein 5000 saal pehle hui thi.",
    "Zero ka invention India mein mathematician Aryabhatta ne kiya.",
    "India mein 22 official languages hain aur 1600+ dialects.",
    "World ka sabse expensive residence Mukesh Ambani ka Antilia hai Mumbai mein.",
    "Kumbh Mela space se bhi dikhta hai! Duniya ka sabse bada gathering.",
]


class FactsProvider(IContentProvider):
    """Facts fetcher with curated Indian facts."""
    
    def __init__(self, config):
        self.config = config
    
    async def fetch_content(self, limit: int = 10) -> List[ContentItem]:
        """Fetch interesting facts."""
        log_step("Fetching facts")
        
        items = []
        
        # Try UselessFacts API
        try:
            response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
            if response.status_code == 200:
                data = response.json()
                fact_text = data.get('text', '')
                
                if fact_text:
                    item = ContentItem(
                        id=f"fact_{hash(fact_text)}",
                        type="fact",
                        title=fact_text[:50],
                        body=fact_text,
                        source="UselessFacts API",
                        score=await self.score_virality(fact_text),
                        created_at=datetime.now()
                    )
                    items.append(item)
        except Exception as e:
            logger.warning(f"UselessFacts API failed: {e}")
        
        # Add curated Indian facts
        needed = limit - len(items)
        if needed > 0:
            selected = random.sample(INDIAN_FACTS, min(needed, len(INDIAN_FACTS)))
            
            for fact in selected:
                item = ContentItem(
                    id=f"indian_fact_{hash(fact)}",
                    type="fact",
                    title=fact[:50],
                    body=fact,
                    source="Curated Indian Facts",
                    score=80.0,
                    created_at=datetime.now()
                )
                items.append(item)
        
        log_success(f"Fetched {len(items)} facts")
        return items[:limit]
    
    async def score_virality(self, fact: str) -> float:
        """Score fact virality."""
        score = 65
        
        # Shorter facts are better
        if len(fact) < 100:
            score += 15
        
        # Numbers and statistics boost engagement
        if any(char.isdigit() for char in fact):
            score += 10
        
        return min(score, 100)
