# Ingestion Module
from .email_fetcher import fetch_threads, normalize_email_thread
from .attachment_extractor import extract_attachments, is_supported_attachment
from .gmail_client import GmailClient
from .outlook_client import OutlookClient

__all__ = [
    "fetch_threads",
    "normalize_email_thread",
    "extract_attachments",
    "is_supported_attachment",
    "GmailClient",
    "OutlookClient",
]
