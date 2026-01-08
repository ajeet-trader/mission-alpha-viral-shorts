"""
Supabase Database Provider

PostgreSQL database with real-time capabilities.
"""

from supabase import create_client, Client
from typing import Dict, List, Optional
import os
from app.core.interfaces import IDatabaseProvider
from app.core.logger import log_step, log_success
import logging

logger = logging.getLogger(__name__)


class SupabaseProvider(IDatabaseProvider):
    """Supabase database provider."""
    
    def __init__(self, config):
        self.config = config
        url = os.getenv('SUPABASE_URL') or config.supabase.url
        key = os.getenv('SUPABASE_KEY') or config.supabase.key
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY required")
        
        self.client: Client = create_client(url, key)
        log_success("Supabase connected")
    
    async def insert(self, table: str, data: Dict) -> str:
        """Insert record."""
        log_step(f"💾 Inserting into {table}")
        result = self.client.table(table).insert(data).execute()
        return result.data[0].get('id') if result.data else None
    
    async def query(self, table: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Query records."""
        log_step(f"🔍 Querying {table}")
        query = self.client.table(table).select("*")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.data
    
    async def update(self, table: str, id: str, data: Dict) -> bool:
        """Update record."""
        log_step(f"📝 Updating {table}/{id}")
        result = self.client.table(table).update(data).eq('id', id).execute()
        return len(result.data) > 0
