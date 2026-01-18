"""
Email Fetcher
-------------
Fetches emails from Gmail/Outlook and converts to EmailThreadV1 contracts.

This is the main entry point for the Ingestion layer.
Output: EmailThreadV1 (Boundary Contract)
"""

from typing import List
from datetime import datetime

from contracts import EmailThreadV1, EmailMessage, AttachmentRef


async def fetch_threads(
    user_id: str,
    provider: str,
    access_token: str,
    max_results: int = 50,
) -> List[EmailThreadV1]:
    """
    Fetch email threads from provider.
    
    Args:
        user_id: Internal user ID
        provider: 'gmail' or 'outlook'
        access_token: OAuth access token
        max_results: Maximum threads to fetch
        
    Returns:
        List of EmailThreadV1 contracts
    """
    if provider == "gmail":
        return await _fetch_gmail_threads(access_token, max_results)
    elif provider == "outlook":
        return await _fetch_outlook_threads(access_token, max_results)
    else:
        raise ValueError(f"Unknown provider: {provider}")


async def _fetch_gmail_threads(access_token: str, max_results: int) -> List[EmailThreadV1]:
    """Fetch threads from Gmail API."""
    # TODO: Implement Gmail API integration
    # 1. Use googleapiclient to list threads
    # 2. For each thread, get full thread data
    # 3. Convert to EmailThreadV1 contract
    raise NotImplementedError("Implement Gmail thread fetching")


async def _fetch_outlook_threads(access_token: str, max_results: int) -> List[EmailThreadV1]:
    """Fetch threads from Outlook/Microsoft Graph API."""
    # TODO: Implement Outlook API integration
    # 1. Use Microsoft Graph API to list conversations
    # 2. For each conversation, get messages
    # 3. Convert to EmailThreadV1 contract
    raise NotImplementedError("Implement Outlook thread fetching")


def normalize_email_thread(
    external_id: str,
    subject: str,
    messages: List[dict],
    attachments: List[dict],
    provider: str,
) -> EmailThreadV1:
    """
    Normalize raw API response to EmailThreadV1 contract.
    
    This ensures all provider-specific junk is stripped out.
    """
    thread_id = f"thread-{external_id}"
    
    normalized_messages = [
        EmailMessage(
            message_id=f"msg-{m.get('id', '')}",
            from_address=m.get("from", ""),
            to_addresses=m.get("to", []),
            cc_addresses=m.get("cc", []),
            subject=m.get("subject", subject),
            body_text=m.get("body_text", ""),
            sent_at=m.get("sent_at", datetime.utcnow()),
            is_from_user=m.get("is_from_user", False),
        )
        for m in messages
    ]
    
    normalized_attachments = [
        AttachmentRef(
            attachment_id=f"att-{a.get('id', '')}",
            filename=a.get("filename", "unknown"),
            original_filename=a.get("original_filename", a.get("filename", "unknown")),
            mime_type=a.get("mime_type", "application/octet-stream"),
            storage_path=a.get("storage_path", ""),
            size_bytes=a.get("size_bytes", 0),
        )
        for a in attachments
    ]
    
    participants = list(set(
        [m.from_address for m in normalized_messages] +
        [addr for m in normalized_messages for addr in m.to_addresses]
    ))
    
    last_updated = max(
        (m.sent_at for m in normalized_messages),
        default=datetime.utcnow()
    )
    
    return EmailThreadV1(
        thread_id=thread_id,
        external_id=external_id,
        subject=subject,
        participants=participants,
        messages=normalized_messages,
        attachments=normalized_attachments,
        last_updated=last_updated,
        provider=provider,
    )
