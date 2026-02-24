# Ingestion Module
from .sync_service import IngestionService
from .gmail_client import GmailClient
from .email_fetcher import fetch_threads, fetch_incremental_changes

__all__ = [
    "IngestionService",
    "GmailClient",
    "fetch_threads",
    "fetch_incremental_changes"
]
