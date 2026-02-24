"""
API Routes - Webhooks
---------------------
Handles incoming webhooks from external providers (e.g., Google Cloud Pub/Sub).
"""

import base64
import json
import logging
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.storage.database import get_db
from models.connected_account import ConnectedAccount, ProviderType
from core.ingestion import IngestionService

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)


@router.post("/gmail")
async def gmail_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive push notifications from Google Cloud Pub/Sub for Gmail changes.
    Expected JSON payload follows the Pub/Sub push format:
    {
      "message": {
        "data": "base64-encoded-json-string",
        "messageId": "12345",
        "publishTime": "2023-01-01T00:00:00Z"
      },
      "subscription": "projects/my-project/subscriptions/my-sub"
    }
    """
    try:
        body = await request.json()
        message = body.get("message", {})
        data_b64 = message.get("data")
        
        if not data_b64:
            logger.warning("Received Gmail webhook without data payload")
            return {"status": "ignored", "reason": "no data"}
            
        # Decode the pub/sub payload
        # Pad with '=' to ensure correct base64 decoding if truncated
        padding = '=' * (4 - len(data_b64) % 4)
        decoded_bytes = base64.urlsafe_b64decode(data_b64 + padding)
        payload = json.loads(decoded_bytes.decode('utf-8'))
        
        email_address = payload.get("emailAddress")
        history_id = payload.get("historyId")
        
        if not email_address:
            logger.warning("Gmail webhook payload missing emailAddress")
            return {"status": "ignored", "reason": "missing emailAddress"}
            
        logger.info(f"🔔 Webhook received for {email_address} (History ID: {history_id})")
        
        # Look up the user by the connected account email
        stmt = select(ConnectedAccount).where(
            ConnectedAccount.provider_email == email_address,
            ConnectedAccount.provider == ProviderType.GMAIL,
            ConnectedAccount.deleted_at == None # noqa: E711
        )
        result = await db.execute(stmt)
        account = result.scalars().first()
        
        if not account:
            logger.warning(f"Webhook received for unknown email: {email_address}")
            return {"status": "ignored", "reason": "unknown account"}
            
        # Trigger background sync for the user
        service = IngestionService(db)
        background_tasks.add_task(service.sync_user_emails, account.user_id)
        
        return {"status": "success", "message": "Sync triggered"}
        
    except Exception as e:
        logger.error(f"Error processing Gmail webhook: {e}")
        # Return 200 anyway so Pub/Sub doesn't infinitely retry malformed messages
        return {"status": "error", "message": str(e)}

