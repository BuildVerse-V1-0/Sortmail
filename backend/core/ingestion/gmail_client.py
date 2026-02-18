"""
Gmail API Client
----------------
Low-level client for Gmail API operations.
"""

from typing import List, Optional
from datetime import datetime


class GmailClient:
    """Gmail API client wrapper."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self._service = None
    
    async def initialize(self):
        """Initialize the Gmail API service."""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials(token=self.access_token)
        # cache_discovery=False recommended to avoid file cache issues in some envs
        self._service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
    
    async def get_profile(self) -> dict:
        """Get user profile."""
        if not self._service:
            await self.initialize()
            
        return self._service.users().getProfile(userId='me').execute()
    
    async def list_threads(
        self,
        max_results: int = 50,
        page_token: Optional[str] = None,
        include_spam_trash: bool = False,
        query: Optional[str] = None
    ) -> dict:
        """List email threads."""
        if not self._service:
            await self.initialize()
            
        kwargs = {
            'userId': 'me',
            'maxResults': max_results,
            'includeSpamTrash': include_spam_trash,
        }
        if page_token:
            kwargs['pageToken'] = page_token
        if query:
            kwargs['q'] = query
            
        return self._service.users().threads().list(**kwargs).execute()
    
    async def get_thread(self, thread_id: str) -> dict:
        """Get a single thread with all messages."""
        if not self._service:
            await self.initialize()
            
        return self._service.users().threads().get(
            userId='me',
            id=thread_id,
            format='full'
        ).execute()
    
    async def get_attachment(
        self,
        message_id: str,
        attachment_id: str,
    ) -> bytes:
        """Download an attachment."""
        if not self._service:
            await self.initialize()
            
        attachment = self._service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()
        
        import base64
        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
        return file_data
    
    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
    ) -> str:
        """Create a draft email."""
        if not self._service:
            await self.initialize()
            
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        if thread_id:
            # If replying to a thread, set References/In-Reply-To if we had the last message ID
            # But here we assume basic threading by subject/threadId for the draft container
            pass

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body = {'message': {'raw': raw_message}}
        
        if thread_id:
            body['message']['threadId'] = thread_id
            
        draft = self._service.users().drafts().create(
            userId='me', 
            body=body
        ).execute()
        
        return draft['id']
