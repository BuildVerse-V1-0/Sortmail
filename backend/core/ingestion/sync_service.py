"""
Sync Service
------------
Orchestrates the fetching and storage of emails.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from contracts import EmailThreadV1
from models.thread import Thread, Message
from models.attachment import Attachment
from models.connected_account import ConnectedAccount, ProviderType
from core.ingestion.email_fetcher import fetch_threads
from core.ingestion.attachment_extractor import extract_attachments

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_user_emails(self, user_id: str):
        """
        Sync emails for a user from all connected accounts.
        """
        # 1. Get connected accounts
        stmt = select(ConnectedAccount).where(ConnectedAccount.user_id == user_id)
        result = await self.db.execute(stmt)
        accounts = result.scalars().all()

        if not accounts:
            logger.info(f"No connected accounts found for user {user_id}")
            return

        for account in accounts:
            try:
                await self._sync_account(account)
            except Exception as e:
                logger.error(f"Failed to sync account {account.id}: {e}")

    async def _sync_account(self, account: ConnectedAccount):
        """
        Sync a single connected account with incremental logic and state management.
        """
        logger.info(f"Syncing account {account.id} ({account.provider})")
        
        # 0. Check State
        # If stuck in syncing for > 1 hour, assume failed and reset (simple recovery)
        if account.sync_status == "syncing":
             if account.last_sync_at and (datetime.utcnow() - account.last_sync_at).total_seconds() < 3600:
                 logger.info(f"Account {account.id} is already syncing. Skipping.")
                 return
             logger.warning(f"Account {account.id} stuck in syncing. Resetting.")

        from core.auth.token_manager import get_valid_google_token, TokenRevokedError
        from core.ingestion.gmail_client import GmailClient
        from core.ingestion.email_fetcher import fetch_incremental_changes

        try:
            # 1. Update State
            account.sync_status = "syncing"
            account.sync_error = None
            account.last_sync_at = datetime.utcnow() # Mark start time
            await self.db.commit()

            # 2. Get Secure Token
            if account.provider == ProviderType.GMAIL:
                access_token = await get_valid_google_token(account.user_id)
                client = GmailClient(access_token, account.user_id)
                await client.initialize()
            else:
                # TODO: Implement Outlook token manager
                logger.warning("Outlook sync not yet fully implemented")
                return

            # 3. Get Current History ID
            profile = await client.get_profile()
            current_history_id = profile.get('historyId')
            
            threads = []
            
            # 4. Sync Strategy
            if account.last_history_id:
                try:
                    logger.info(f"Attempting incremental sync for {account.id} from {account.last_history_id}")
                    threads = await fetch_incremental_changes(
                        user_id=account.user_id,
                        provider=account.provider.value,
                        access_token=access_token,
                        start_history_id=account.last_history_id,
                        client=client
                    )
                except Exception as e:
                    logger.warning(f"Incremental sync failing, falling back to full sync: {e}")
                    account.last_history_id = None # Force full sync
            
            # Fallback or Full Sync
            if not threads and not account.last_history_id:
                logger.info(f"Performing full sync for {account.id}")
                threads = await fetch_threads(
                    user_id=account.user_id,
                    provider=account.provider.value,
                    access_token=access_token,
                    max_results=100,
                    client=client
                )

            # 5. Persist Data
            if threads:
                for thread_contract in threads:
                    await self._save_thread(account.user_id, thread_contract, client)
                logger.info(f"Synced {len(threads)} threads for account {account.id}")

            # 6. Success State
            account.sync_status = "idle"
            account.last_history_id = current_history_id
            account.last_sync_at = datetime.utcnow()
            await self.db.commit()

        except TokenRevokedError:
            logger.error(f"Token revoked for account {account.id}")
            account.sync_status = "revoked"
            account.sync_error = "Access revoked"
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Sync failed for account {account.id}: {e}")
            account.sync_status = "failed"
            account.sync_error = str(e)
            await self.db.commit()


    async def _save_thread(self, user_id: str, contract: EmailThreadV1, client=None):
        """
        Upsert thread and its messages/attachments.
        """
        # 3a. Upsert Thread
        stmt = select(Thread).where(
            Thread.user_id == user_id, 
            Thread.external_id == contract.external_id
        )
        result = await self.db.execute(stmt)
        thread = result.scalars().first()

        if not thread:
            thread = Thread(
                id=contract.thread_id,
                user_id=user_id,
                external_id=contract.external_id,
                provider=contract.provider,
                created_at=datetime.utcnow()
            )
            self.db.add(thread)
        
        # Update mutable fields
        thread.subject = contract.subject
        thread.participants = contract.participants
        thread.last_email_at = contract.last_updated
        thread.last_synced_at = datetime.utcnow()
        
        # Meta (New)
        thread.labels = contract.labels
        thread.is_unread = 1 if contract.is_unread else 0
        thread.is_starred = contract.is_starred
        thread.has_attachments = len(contract.attachments) > 0
        
        # 3b. Upsert Messages
        for msg_contract in contract.messages:
            msg_stmt = select(Message).where(
                Message.thread_id == thread.id,
                Message.id == msg_contract.message_id
            )
            result = await self.db.execute(msg_stmt)
            msg = result.scalars().first()

            if not msg:
                msg = Message(
                    id=msg_contract.message_id,
                    thread_id=thread.id,
                    from_address=msg_contract.from_address,
                    to_addresses=msg_contract.to_addresses,
                    cc_addresses=msg_contract.cc_addresses,
                    subject=msg_contract.subject,
                    body_text=msg_contract.body_text,
                    is_from_user=str(msg_contract.is_from_user).lower(), 
                    sent_at=msg_contract.sent_at,
                    created_at=datetime.utcnow()
                )
                self.db.add(msg)
                await self.db.flush() 

        # 3c. Upsert Attachments
        from core.ingestion.attachment_extractor import _store_attachment

        for att_contract in contract.attachments:
            # Check if attachment exists
            att_stmt = select(Attachment).where(Attachment.id == att_contract.attachment_id)
            result = await self.db.execute(att_stmt)
            att = result.scalars().first()

            storage_path = att_contract.storage_path
            
            # Download if missing and client available
            if not storage_path and client and att_contract.size_bytes < 25 * 1024 * 1024:
                try:
                    # remove 'msg-' prefix from message_id if needed, check contract
                    # contracts uses 'msg-ID'. Gmail API expects raw ID.
                    # fetcher adds 'msg-' prefix.
                    # We need RAW message ID.
                    raw_msg_id = att_contract.message_id.replace("msg-", "")
                    # Same for att_id? fetcher adds 'att-'.
                    raw_att_id = att_contract.attachment_id.replace("att-", "")
                    
                    file_data = await client.get_attachment(raw_msg_id, raw_att_id)
                    if file_data:
                         # Store locally
                        storage_path = await _store_attachment(
                            user_id, 
                            att_contract.filename, 
                            file_data
                        )
                except Exception as e:
                    logger.error(f"Failed to download attachment {att_contract.attachment_id}: {e}")

            if not att:
                att = Attachment(
                    id=att_contract.attachment_id,
                    message_id=att_contract.message_id,
                    user_id=user_id,
                    filename=att_contract.filename,
                    original_filename=att_contract.original_filename,
                    mime_type=att_contract.mime_type,
                    size_bytes=att_contract.size_bytes,
                    storage_path=storage_path, # UPDATED
                    created_at=datetime.utcnow()
                )
                self.db.add(att)
            elif storage_path and not att.storage_path:
                att.storage_path = storage_path
        
        await self.db.commit()
