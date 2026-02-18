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
    from .gmail_client import GmailClient
    
    client = GmailClient(access_token)
    await client.initialize()
    
    # 1. List threads
    response = await client.list_threads(max_results=max_results, include_spam_trash=False)
    threads_list = response.get('threads', [])
    
    results = []
    
    # 2. Get full thread details
    for thread_meta in threads_list:
        try:
            thread_data = await client.get_thread(thread_meta['id'])
            
            # 3. Parse messages
            parsed_messages = []
            all_attachments = []
            
            messages_data = thread_data.get('messages', [])
            if not messages_data:
                continue
                
            subject = ""
            
            for msg in messages_data:
                parsed_msg, msg_attachments = _parse_gmail_message(msg)
                parsed_messages.append(parsed_msg)
                all_attachments.extend(msg_attachments)
                
                # Use the subject from the first message (or any that has it)
                if not subject and parsed_msg.get('subject'):
                    subject = parsed_msg['subject']
            
            # 4. Normalize
            thread_contract = normalize_email_thread(
                external_id=thread_data['id'],
                subject=subject,
                messages=parsed_messages,
                attachments=all_attachments,
                provider='gmail'
            )
            results.append(thread_contract)
            
        except Exception as e:
            print(f"Error processing thread {thread_meta.get('id')}: {e}")
            continue
            
    return results


def _parse_gmail_message(msg_resource: dict) -> tuple[dict, List[dict]]:
    """Parse a raw Gmail message resource into a simplified dict and attachments list."""
    payload = msg_resource.get('payload', {})
    headers = payload.get('headers', [])
    
    # Extract headers
    header_map = {h['name'].lower(): h['value'] for h in headers}
    
    # Extract body
    body_text = _extract_body(payload)
    
    # Extract attachments
    attachments = _extract_attachments_metadata(payload, msg_resource.get('id'))
    
    parsed_msg = {
        'id': msg_resource.get('id'),
        'threadId': msg_resource.get('threadId'),
        'from': header_map.get('from', ''),
        'to': [addr.strip() for addr in header_map.get('to', '').split(',') if addr.strip()],
        'cc': [addr.strip() for addr in header_map.get('cc', '').split(',') if addr.strip()],
        'subject': header_map.get('subject', ''),
        'body_text': body_text,
        'sent_at': datetime.fromtimestamp(int(msg_resource.get('internalDate', 0)) / 1000),
        'is_from_user': 'SENT' in msg_resource.get('labelIds', []),
    }
    
    return parsed_msg, attachments


def _extract_body(payload: dict) -> str:
    """Extract text body from multipart payload."""
    import base64
    
    body = ""
    
    if payload.get('mimeType') == 'text/plain':
        data = payload.get('body', {}).get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
            
    parts = payload.get('parts', [])
    for part in parts:
        if part.get('mimeType') == 'text/plain':
            data = part.get('body', {}).get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        elif part.get('mimeType') == 'multipart/alternative':
            # Recursive check for text/plain inside multipart/alternative
            return _extract_body(part)
            
    # Fallback: if no text/plain found, look for text/html
    if not body:
        for part in parts:
             if part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data')
                if data:
                    # Strip tags if needed, or return HTML. 
                    # For now returning raw HTML as body_text might be messy but better than nothing.
                    # Or better: keep searching.
                    pass 
    
    return body


def _extract_attachments_metadata(payload: dict, message_id: str) -> List[dict]:
    """Extract metadata for attachments."""
    attachments = []
    parts = payload.get('parts', [])
    
    for part in parts:
        filename = part.get('filename')
        if filename:
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')
            if attachment_id:
                attachments.append({
                    'id': attachment_id,
                    'message_id': message_id,
                    'filename': filename,
                    'mime_type': part.get('mimeType'),
                    'size_bytes': body.get('size', 0),
                    # data is NOT included here, fetched on demand
                })
        
        # Recurse if multipart
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
