"""
Reddit Content Provider Plugin

Scrapes Reddit for viral content with fallback to web scraping.
"""

import praw
from typing import List
from datetime import datetime
from app.core.interfaces import IContentProvider, ContentItem
from app.core.logger import log_step, log_success, log_warning
import logging
import os

logger = logging.getLogger(__name__)


class RedditProvider(IContentProvider):
    """Reddit content scraper with API and web scraping fallback."""
    
    def __init__(self, config):
        self.config = config
        self.reddit = None
        self._init_reddit()
    
    def _init_reddit(self):
        """Initialize Reddit API if credentials available."""
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        if client_id and client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent='Mission Alpha Shorts Factory v2.0'
                )
                log_success("Reddit API initialized")
            except Exception as e:
                log_warning(f"Reddit API init failed: {e}. Will use web scraping.")
    
    async def fetch_content(self, limit: int = 10) -> List[ContentItem]:
        """Fetch content from Reddit."""
        log_step("Fetching content from Reddit", 
                f"Subreddits: {', '.join(self.config.reddit.subreddits)}")
        
        items = []
        
        for subreddit_name in self.config.reddit.subreddits:
            try:
                if self.reddit:
                    # Use API
                    subreddit = self.reddit.subreddit(subreddit_name)
                    posts = subreddit.hot(limit=limit)
                    
                    for post in posts:
                        if post.ups >= self.config.reddit.min_upvotes:
                            item = ContentItem(
                                id=f"reddit_{post.id}",
                                type="story",
                                title=post.title,
                                body=post.selftext if post.selftext else post.title,
                                source=f"r/{subreddit_name}",
                                score=await self.score_virality(post),
                                created_at=datetime.fromtimestamp(post.created_utc)
                            )
                            items.append(item)
                            
                            if len(items) >= limit:
                                break
                else:
                    # Fallback: web scraping
                    log_warning("Using web scraping fallback (no API credentials)")
                    # TODO: Implement web scraping
                    
            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit_name}: {e}")
        
        log_success(f"Fetched {len(items)} items from Reddit")
        return items[:limit]
    
    async def score_virality(self, post) -> float:
        """Score Reddit post virality (0-100)."""
        # Simple scoring: upvotes + comments + awards
        score = (
            (post.ups / 1000) * 40 +  # Max 40 points for upvotes
            (post.num_comments / 100) * 30 +  # Max 30 for comments
            (post.total_awards_received * 10)  # 10 points per award
        )
        return min(score, 100)
