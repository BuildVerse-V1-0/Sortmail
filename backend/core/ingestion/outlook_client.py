"""
Outlook API Client
------------------
Low-level client for Microsoft Graph API (Outlook).
"""

from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OutlookClient:
    """Microsoft Graph API client for Outlook."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self._base_url = "https://graph.microsoft.com/v1.0"
    
    async def list_conversations(
        self,
        max_results: int = 50,
        skip: int = 0,
    ) -> dict:
        """List email conversations."""
        logger.warning("Microsoft Graph API / Outlook sync is not yet implemented.")
        return {"value": []}
    
    async def get_message(self, message_id: str) -> dict:
        """Get a single message with details."""
        logger.warning("Microsoft Graph API / Outlook message fetch is not yet implemented.")
        return {}
    
    async def get_attachment(
        self,
        message_id: str,
        attachment_id: str,
    ) -> bytes:
        """Download an attachment."""
        logger.warning("Microsoft Graph API / Outlook attachment download is not yet implemented.")
        return b""
    
    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Create a draft email."""
        logger.warning("Microsoft Graph API / Outlook draft creation is not yet implemented.")
        return ""
