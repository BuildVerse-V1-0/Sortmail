"""
API Routes - Attachments
------------------------
Endpoints for previewing and downloading email attachments.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from core.storage.database import get_db
from models.attachment import Attachment
from models.user import User
from models.email import Email
from api.dependencies import get_current_user
from core.auth.token_manager import get_valid_google_token
from core.ingestion.gmail_client import GmailClient
from core.ingestion.attachment_extractor import _store_attachment

logger = logging.getLogger(__name__)

router = APIRouter()

async def _fetch_fallback_attachment(attachment: Attachment, user_id: str, db: AsyncSession):
    """Fallback fetcher when local storage is wiped (e.g., ephemeral Railway deploys)."""
    try:
        # Get the email to find the true external message ID
        stmt = select(Email).where(Email.id == attachment.email_id)
        result = await db.execute(stmt)
        email = result.scalars().first()
        if not email:
            logger.error(f"Fallback: Parent email {attachment.email_id} not found")
            return None

        msg_id = email.external_id
        raw_att_id = attachment.id.replace("att-", "")

        # Fetch valid token & initialize client
        token = await get_valid_google_token(user_id)
        if not token:
            logger.error(f"Fallback: Could not retrieve valid Google token for user {user_id}")
            return None
            
        client = GmailClient(token, user_id)
        await client.initialize()

        logger.info(f"Fallback: Fetching missing attachment bytes live from Gmail (msg: {msg_id}, att: {raw_att_id})")
        file_bytes = await client.get_attachment(msg_id, raw_att_id)
        if not file_bytes:
            return None

        # Re-cache locally
        storage_path = await _store_attachment(user_id, attachment.filename_sanitized, file_bytes)
        
        # Update DB pointer
        attachment.storage_path = storage_path
        await db.commit()
        
        return file_bytes
    except Exception as e:
        logger.error(f"Fallback fetch failed for {attachment.id}: {e}")
        return None


@router.get("/{attachment_id}/preview")
async def preview_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Preview an attachment in the browser (inline).
    Suitable for images, PDFs, etc.
    """
    stmt = select(Attachment).where(
        Attachment.id == attachment_id,
        Attachment.user_id == current_user.id
    )
    result = await db.execute(stmt)
    attachment = result.scalars().first()

    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    if not attachment.storage_path or not os.path.exists(attachment.storage_path):
        # Attempt fallback
        file_bytes = await _fetch_fallback_attachment(attachment, current_user.id, db)
        if file_bytes:
            return Response(
                content=file_bytes,
                media_type=attachment.mime_type or "application/octet-stream",
                headers={"Content-Disposition": f'inline; filename="{attachment.filename}"'}
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment file not found on server")

    return FileResponse(
        path=attachment.storage_path,
        media_type=attachment.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{attachment.filename}"'}
    )


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download an attachment (forces save dialog).
    """
    stmt = select(Attachment).where(
        Attachment.id == attachment_id,
        Attachment.user_id == current_user.id
    )
    result = await db.execute(stmt)
    attachment = result.scalars().first()

    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    if not attachment.storage_path or not os.path.exists(attachment.storage_path):
        # Attempt fallback
        file_bytes = await _fetch_fallback_attachment(attachment, current_user.id, db)
        if file_bytes:
            return Response(
                content=file_bytes,
                media_type=attachment.mime_type or "application/octet-stream",
                headers={"Content-Disposition": f'attachment; filename="{attachment.filename}"'}
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment file not found on server")

    return FileResponse(
        path=attachment.storage_path,
        media_type=attachment.mime_type or "application/octet-stream",
        filename=attachment.filename
    )
