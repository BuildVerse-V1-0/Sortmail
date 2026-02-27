"""
Email Fetcher
-------------
Fetches emails from Gmail/Outlook and converts to EmailThreadV1 contracts.
Production-grade: Robust MIME parsing, Size limits, Rate limiting integration.

This is the main entry point for the Ingestion layer.
Output: EmailThreadV1 (Boundary Contract)
"""

from typing import List, Optional, Tuple
from datetime import datetime, timezone
import logging

from contracts import EmailThreadV1, EmailMessage, AttachmentRef
from .gmail_client import GmailClient, TokenRevokedError

logger = logging.getLogger(__name__)

# Constants
MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

async def fetch_threads(
    user_id: str,
    provider: str,
    access_token: str,
    max_results: int = 50,
    client: Optional[object] = None
) -> List[EmailThreadV1]:
    """
    Fetch email threads from provider.
    """
    if provider == "gmail":
        return await _fetch_gmail_threads(user_id, access_token, max_results, client)
    elif provider == "outlook":
        return await _fetch_outlook_threads(access_token, max_results)
    else:
        raise ValueError(f"Unknown provider: {provider}")


async def fetch_incremental_changes(
    user_id: str,
    provider: str,
    access_token: str,
    start_history_id: str,
    client: Optional[object] = None
) -> List[EmailThreadV1]:
    """
    Fetch changes since a specific history ID.
    """
    if provider != "gmail":
         return await fetch_threads(user_id, provider, access_token, max_results=20, client=client)

    if not client:
        client = GmailClient(access_token, user_id)
        await client.initialize()

    changed_thread_ids = set()
    page_token = None
    
    while True:
        try:
            # Request all history types to avoid dropping label changes or messages
            history_data = await client.get_history(start_history_id, page_token=page_token)
        except Exception as e:
            logger.warning(f"Incremental sync failed or partially failed for user {user_id} (historyId {start_history_id}): {e}")
            break # Process whatever we managed to fetch so far

        for record in history_data.get('history', []):
            # Handle new messages
            for msg_added in record.get('messagesAdded', []):
                if 'message' in msg_added and 'threadId' in msg_added['message']:
                    changed_thread_ids.add(msg_added['message']['threadId'])
                    
            # Handle label changes (e.g. marking as read/unread, or archiving)
            for label_added in record.get('labelsAdded', []):
                 if 'message' in label_added and 'threadId' in label_added['message']:
                    changed_thread_ids.add(label_added['message']['threadId'])
                    
            for label_removed in record.get('labelsRemoved', []):
                 if 'message' in label_removed and 'threadId' in label_removed['message']:
                    changed_thread_ids.add(label_removed['message']['threadId'])
                    
        page_token = history_data.get('nextPageToken')
        if not page_token:
            break

    if not changed_thread_ids:
        return []
        
    results = []
    # Limit incremental batch size to prevent timeouts
    thread_ids_list = list(changed_thread_ids)[:50] 
    
    for thread_id in thread_ids_list:
        try:
            thread_data = await client.get_thread(thread_id)
            if not thread_data.get('messages'):
                continue
                
            thread_contract = _parse_and_normalize_thread(thread_data, 'gmail')
            results.append(thread_contract)

        except TokenRevokedError:
            raise # Propagate specific auth errors
        except Exception as e:
            if "404" in str(e) and "notFound" in str(e):
                logger.warning(f"Incremental thread {thread_id} not found (404). Probably deleted. Skipping.")
                continue
            logger.error(f"Error processing incremental thread {thread_id}: {e}")
            continue

    return results


async def _fetch_gmail_threads(
    user_id: str,
    access_token: str,
    max_results: int,
    client: Optional[object] = None
) -> List[EmailThreadV1]:
    """Fetch threads from Gmail API."""
    if not client:
        client = GmailClient(access_token, user_id)
        await client.initialize()
    
    # 1. List threads
    try:
        response = await client.list_threads(max_results=max_results, include_spam_trash=False)
    except TokenRevokedError:
        raise
    except Exception as e:
        logger.error(f"Failed to list threads for user {user_id}: {e}")
        return []
        
    threads_list = response.get('threads', [])
    results = []
    
    # 2. Get full thread details
    for thread_meta in threads_list:
        try:
            thread_data = await client.get_thread(thread_meta['id'])
            if not thread_data.get('messages'):
                continue
                
            thread_contract = _parse_and_normalize_thread(thread_data, 'gmail')
            results.append(thread_contract)
            
        except TokenRevokedError:
            raise
        except Exception as e:
            if "404" in str(e) and "notFound" in str(e):
                logger.warning(f"Thread {thread_meta.get('id')} not found (404). Probably deleted. Skipping.")
                continue
            logger.error(f"Error processing thread {thread_meta.get('id')}: {e}")
            continue
            
    return results

def _parse_and_normalize_thread(thread_data: dict, provider: str) -> EmailThreadV1:
    """Shared logic for parsing a thread response."""
    messages_data = thread_data.get('messages', [])
    
    parsed_messages = []
    all_attachments = []
    subject = ""
    
    for msg in messages_data:
        parsed_msg, msg_attachments = _parse_gmail_message(msg)
        parsed_messages.append(parsed_msg)
        all_attachments.extend(msg_attachments)
        
        # Use simple heuristic for subject: first message or non-empty
        if not subject and parsed_msg.get('subject'):
            subject = parsed_msg['subject']
            
    return normalize_email_thread(
        external_id=thread_data['id'],
        subject=subject,
        messages=parsed_messages,
        attachments=all_attachments,
        provider=provider
    )


def _parse_gmail_message(msg_resource: dict) -> Tuple[dict, List[dict]]:
    """Parse a raw Gmail message resource into a simplified dict and attachments list."""
    payload = msg_resource.get('payload', {})
    headers = payload.get('headers', [])
    
    # Extract headers efficiently
    header_map = {h['name'].lower(): h['value'] for h in headers}
    
    # 1. Fallback Strategy for Missing "From" Field (Automated Newsletters/System emails)
    from_address = header_map.get('from', '').strip()
    if not from_address:
        # Try finding the designated sender alias
        from_address = header_map.get('sender', '').strip()
    if not from_address:
        # Try finding the envelope return path (usually contains the raw sender logic)
        from_address = header_map.get('return-path', '').strip()
    if not from_address:
         # Try finding Reply-To
         from_address = header_map.get('reply-to', '').strip()
    
    # If it is still brutally empty, we log it and assign a strict internal fallback 
    # so we don't violate PostgreSQL NOT NULL constraints downstream.
    if not from_address:
        logger.warning(f"Message {msg_resource.get('id')} has no discernible sender headers. Using system fallback.")
        from_address = "unknown-sender@sortmail.internal"

    # Extract body with enhanced MIME recursion
    body_text, body_html = _extract_body(payload)
    
    # Extract attachments with size limits
    attachments = _extract_attachments_metadata(payload, msg_resource.get('id'))
    
    from email.utils import parsedate_to_datetime
    
    # 2. Extract Dates defensively
    date_raw = header_map.get('date', '').strip()
    sent_at = None
    if date_raw:
        try:
            sent_at = parsedate_to_datetime(date_raw)
            # Ensure it's offset-aware UTC for our DB
            if sent_at.tzinfo is None:
                sent_at = sent_at.replace(tzinfo=timezone.utc)
            else:
                sent_at = sent_at.astimezone(timezone.utc)
        except Exception:
            pass
            
    # internalDate is always when Gmail received the email
    received_at = datetime.fromtimestamp(int(msg_resource.get('internalDate', 0)) / 1000, tz=timezone.utc)
    
    if not sent_at:
        sent_at = received_at
    
    parsed_msg = {
        'id': msg_resource.get('id'),
        'threadId': msg_resource.get('threadId'),
        'from': from_address,
        'to': [addr.strip() for addr in header_map.get('to', '').split(',') if addr.strip()],
        'cc': [addr.strip() for addr in header_map.get('cc', '').split(',') if addr.strip()],
        'subject': header_map.get('subject', ''),
        'body_text': body_text,
        'body_html': body_html,
        'sent_at': sent_at,
        'received_at': received_at,
        'is_from_user': 'SENT' in msg_resource.get('labelIds', []),
        'labels': msg_resource.get('labelIds', []),
    }
    
    return parsed_msg, attachments


def _extract_body(payload: dict) -> Tuple[str, str]:
    """Recursively extract plain text and HTML body from multipart payload.
    Returns: (body_text, body_html)
    """
    import base64
    
    body_text = ""
    body_html = ""
    mime_type = payload.get('mimeType')
    
    # Direct Key
    if mime_type == 'text/plain':
        data = payload.get('body', {}).get('data')
        if data:
            body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            return body_text, body_html
            
    if mime_type == 'text/html':
        data = payload.get('body', {}).get('data')
        if data:
            body_html = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            return body_text, body_html

    # Multipart handling
    parts = payload.get('parts', [])
    
    # Process sequentially: parts can be alternative (choose best) or mixed (append)
    # Gmail usually sends multipart/alternative with text/plain and text/html
    for part in parts:
        p_mime = part.get('mimeType', '')
        if p_mime == 'text/plain' and not body_text:
            data = part.get('body', {}).get('data')
            if data:
                body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        elif p_mime == 'text/html' and not body_html:
            data = part.get('body', {}).get('data')
            if data:
                # We do NOT sanitize here to preserve exact layout and styles for the UI payload layer.
                body_html = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        elif p_mime.startswith('multipart/'):
            child_text, child_html = _extract_body(part)
            if not body_text and child_text:
                body_text = child_text
            if not body_html and child_html:
                body_html = child_html
                
    return body_text, body_html


def _extract_attachments_metadata(payload: dict, message_id: str) -> List[dict]:
    """Extract metadata for attachments with size checks."""
    attachments = []
    parts = payload.get('parts', [])
    
    for part in parts:
        filename = part.get('filename')
        if filename:
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')
            size_bytes = body.get('size', 0)
            
            # Size Limit Check
            if size_bytes > MAX_ATTACHMENT_SIZE_BYTES:
                logger.warning(f"Skipping oversized attachment '{filename}' ({size_bytes} bytes)")
                continue
                
            if attachment_id:
                attachments.append({
                    'id': attachment_id,
                    'message_id': message_id,
                    'filename': filename,
                    'mime_type': part.get('mimeType'),
                    'size_bytes': size_bytes,
                })
        
        # Recursion for nested parts
        if part.get('parts'):
            attachments.extend(_extract_attachments_metadata(part, message_id))
            
    return attachments


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
            body_html=m.get("body_html", ""),
            sent_at=m.get("sent_at", datetime.now(timezone.utc)),
            received_at=m.get("received_at", datetime.now(timezone.utc)),
            is_from_user=m.get("is_from_user", False),
            labels=m.get("labels", []),
        )
        for m in messages
    ]
    
    normalized_attachments = [
        AttachmentRef(
            attachment_id=f"att-{a.get('id', '')}",
            email_id=f"msg-{a.get('message_id', '')}",
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
        default=lambda: datetime.now(timezone.utc)()
    )
    
    # Aggregate labels from all messages
    all_labels = set()
    for m in normalized_messages:
        all_labels.update(m.labels)
    
    unique_labels = list(all_labels)
    is_unread = "UNREAD" in unique_labels
    is_starred = "STARRED" in unique_labels
    
    return EmailThreadV1(
        thread_id=thread_id,
        external_id=external_id,
        subject=subject,
        participants=participants,
        messages=normalized_messages,
        attachments=normalized_attachments,
        last_updated=last_updated,
        provider=provider,
        labels=unique_labels,
        is_unread=is_unread,
        is_starred=is_starred,
    )
