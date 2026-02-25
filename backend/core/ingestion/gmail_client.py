"""
Gmail API Client
----------------
Low-level client for Gmail API operations.
Production-grade: Rate limiting, Retries, Async execution.
"""

import asyncio
import logging
import functools
from typing import List, Optional, Any, Callable
from googleapiclient.errors import HttpError

from core.ingestion.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class TokenRevokedError(Exception):
    """Raised when the OAuth token is revoked or expired."""
    pass

class GmailClient:
    """
    Gmail API client wrapper.
    Handles auth, rate limiting, and async execution.
    """
    
    def __init__(self, access_token: str, user_id: str):
        self.access_token = access_token
        self.user_id = user_id
        self._service = None
        # Rate Limit: 10 requests/second slightly below Google's 250 quota units/user/sec
        # to leave room for other apps or burst handling.
        self.limiter = RateLimiter(rate=10, capacity=20, namespace="gmail_quota")
    
    async def initialize(self):
        """Initialize the Gmail API service."""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials(token=self.access_token)
        
        # Use run_in_executor for the blocking build() call if needed, 
        # but build() is usually fast. .execute() is the slow part.
        def _build():
            return build('gmail', 'v1', credentials=creds, cache_discovery=False)
            
        loop = asyncio.get_running_loop()
        self._service = await loop.run_in_executor(None, _build)
        
    async def _execute(self, request_factory: Callable[[], Any]) -> Any:
        """
        Execute a Google API request with Rate Limiting, Async Wrapping, and Retries.
        """
        if not self._service:
            await self.initialize()

        # 1. Acquire Rate Limit Token
        await self.limiter.acquire(self.user_id)

        loop = asyncio.get_running_loop()
        retries = 3
        
        for attempt in range(retries):
            try:
                # 2. Construct the request (synchronously)
                request = request_factory()
                
                # 3. Execute in ThreadPool (Async wrapper)
                response = await loop.run_in_executor(None, request.execute)
                return response
                
            except HttpError as e:
                # 401: Token Revoked/Expired
                if e.resp.status == 401:
                    logger.warning(f"Gmail 401 Unauthorized for {self.user_id}")
                    raise TokenRevokedError(f"Access token expired or revoked: {e}")
                
                # 429: Too Many Requests (Rate Limit from Google side)
                # 5xx: Server Errors
                if e.resp.status == 429 or e.resp.status >= 500:
                    wait_time = (2 ** attempt) + 1 # Exponential backoff: 3s, 5s, 9s
                    logger.warning(f"Gmail Error {e.resp.status}, retrying in {wait_time}s... (Attempt {attempt+1}/{retries})")
                    await asyncio.sleep(wait_time)
                    continue
                
                # Other errors (400, 403, 404) -> Raise immediately
                logger.error(f"Gmail API Fatal Error {e.resp.status}: {e}")
                raise e
            except Exception as e:
                # Network errors etc.
                logger.error(f"Unexpected Gmail Client Error: {e}")
                raise e
                
        raise Exception(f"Max retries ({retries}) exceeded for Gmail API call")

    async def get_profile(self) -> dict:
        """Get user profile."""
        return await self._execute(
            lambda: self._service.users().getProfile(userId='me')
        )
    
    async def list_threads(
        self,
        max_results: int = 50,
        page_token: Optional[str] = None,
        include_spam_trash: bool = False,
        query: Optional[str] = None
    ) -> dict:
        """List email threads."""
        kwargs = {
            'userId': 'me',
            'maxResults': max_results,
            'includeSpamTrash': include_spam_trash,
        }
        if page_token:
            kwargs['pageToken'] = page_token
        if query:
            kwargs['q'] = query
            
        return await self._execute(
            lambda: self._service.users().threads().list(**kwargs)
        )
    
    async def get_thread(self, thread_id: str) -> dict:
        """Get a single thread with all messages."""
        return await self._execute(
            lambda: self._service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            )
        )
    
    async def get_attachment(
        self,
        message_id: str,
        attachment_id: str,
    ) -> bytes:
        """Download an attachment."""
        attachment = await self._execute(
            lambda: self._service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            )
        )
        
        import base64
        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
        return file_data
    
    async def get_history(
        self, 
        start_history_id: str, 
        history_types: Optional[List[str]] = None,
        page_token: Optional[str] = None
    ) -> dict:
        """Get history of changes since start_history_id."""
        kwargs = {
            'userId': 'me',
            'startHistoryId': start_history_id
        }
        if history_types:
            kwargs['historyTypes'] = history_types
        if page_token:
            kwargs['pageToken'] = page_token
            
        return await self._execute(
            lambda: self._service.users().history().list(**kwargs)
        )

    async def watch(self, topic_name: str) -> dict:
        """Subscribe to real-time push notifications via Cloud Pub/Sub."""
        return await self._execute(
            lambda: self._service.users().watch(
                userId='me',
                body={'topicName': topic_name}
            )
        )

    async def stop(self) -> None:
        """Stop real-time push notifications."""
        return await self._execute(
            lambda: self._service.users().stop(userId='me')
        )

    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
    ) -> str:
        """Create a draft email."""
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body_payload =({'message': {'raw': raw_message}})
        
        if thread_id:
            body_payload['message']['threadId'] = thread_id
            
        draft = await self._execute(
            lambda: self._service.users().drafts().create(
                userId='me', 
                body=body_payload
            )
        )
        
        return draft['id']
