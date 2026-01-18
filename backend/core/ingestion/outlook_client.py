"""
Outlook API Client
------------------
Low-level client for Microsoft Graph API (Outlook).
"""

from typing import List, Optional
from datetime import datetime


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
        # TODO: Implement using httpx
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"{self._base_url}/me/mailFolders/inbox/messages",
        #         headers={"Authorization": f"Bearer {self.access_token}"},
        #         params={"$top": max_results, "$skip": skip},
        #     )
        #     return response.json()
        raise NotImplementedError("Implement Outlook conversation listing")
    
    async def get_message(self, message_id: str) -> dict:
        """Get a single message with details."""
        # TODO: Implement
        raise NotImplementedError("Implement Outlook message fetch")
    
    async def get_attachment(
        self,
        message_id: str,
        attachment_id: str,
    ) -> bytes:
        """Download an attachment."""
        # TODO: Implement
        raise NotImplementedError("Implement Outlook attachment download")
    
    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Create a draft email."""
        # TODO: Implement
        raise NotImplementedError("Implement Outlook draft creation")
