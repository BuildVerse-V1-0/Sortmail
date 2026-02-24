
import sys
import os
import asyncio
import base64
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Env Vars
import sys
from unittest.mock import MagicMock

# MOCK DATABASE MODULES BEFORE IMPORTING ANYTHING ELSE
mock_storage = MagicMock()
mock_db_module = MagicMock()
mock_db_module.Base = MagicMock # This needs to be a class or usable as base
# Improve Base mock to allow SQLAlchemy models to inherit
from sqlalchemy.orm import declarative_base
mock_db_module.Base = declarative_base()
mock_db_module.get_db = MagicMock()

sys.modules["core.storage"] = mock_storage
sys.modules["core.storage.database"] = mock_db_module
# Also need to make sure core.storage.Base is available if imported from core.storage
mock_storage.Base = mock_db_module.Base

os.environ["GOOGLE_CLIENT_ID"] = "dummy"
os.environ["GOOGLE_CLIENT_SECRET"] = "dummy"
os.environ["STORAGE_PATH"] = "./data/attachments/test" # Test storage path
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db" # Dummy for config
os.environ["SECRET_KEY"] = "dummy-secret-key-for-testing"
os.environ["ALGORITHM"] = "HS256"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/auth/google/callback"
os.environ["MICROSOFT_REDIRECT_URI"] = "http://localhost:8000/auth/microsoft/callback"
os.environ["JWT_SECRET"] = "dummy-jwt-secret"

try:
    print("Importing models.connected_account...")
    import models.connected_account
    print("Importing core.ingestion.sync_service...")
    import core.ingestion.sync_service
    
    print("Importing IngestionService...")
    from core.ingestion.sync_service import IngestionService
    print("Importing GmailClient...")
    from core.ingestion.gmail_client import GmailClient
    print("Importing Thread, Email...")
    from models.thread import Thread
    from models.email import Email
    print("Importing Attachment...")
    from models.attachment import Attachment
    print("Importing User...")
    from models.user import User, EmailProvider
    
    print("Importing core.storage.database...")
    import core.storage.database
    print("Imports successful.")
except ImportError as e:
    import traceback
    traceback.print_exc()
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

async def verify_ingestion_flow():
    # Configure logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("core.ingestion.sync_service")
    logger.setLevel(logging.INFO)

    print("Starting End-to-End Ingestion Flow Verification...")
    
    # 1. Setup Mock Gmail Client Data
    # Malicious HTML Content
    malicious_html = "<h1>Safe Title</h1><script>alert('XSS')</script><p>Safe Body</p>"
    encoded_html = base64.urlsafe_b64encode(malicious_html.encode('utf-8')).decode('utf-8')
    
    # Mock Thread List
    mock_threads_list = {'threads': [{'id': 'thread-123'}]}
    
    # Mock Thread Details
    mock_thread_details = {
        'id': 'thread-123',
        'messages': [
            {
                'id': 'msg-123',
                'threadId': 'thread-123',
                'internalDate': '1700000000000',
                'labelIds': ['INBOX'],
                'payload': {
                    'headers': [
                        {'name': 'From', 'value': 'sender@example.com'},
                        {'name': 'To', 'value': 'user@example.com'},
                        {'name': 'Subject', 'value': 'Test with Malicious HTML'},
                    ],
                    'parts': [
                        {
                            'mimeType': 'text/html',
                            'body': {'data': encoded_html}
                        },
                        {
                            'filename': 'virus.exe', # Should be blocked later, but now we check handling
                            'mimeType': 'application/x-msdownload',
                            'body': {'attachmentId': 'att-1', 'size': 1024}
                        }
                    ]
                }
            }
        ]
    }
    
    # 2. Mock Database Session
    mock_db = AsyncMock()
    
    # Mock DB Execute (Upsert) - Just logging calls
    # mock_db.execute.return_value = None # DON'T set to None, we need to chain it later
    mock_db.commit.return_value = None
    
    # 3. Mock GmailClient methods
    mock_client_instance = AsyncMock(spec=GmailClient)
    mock_client_instance.initialize.return_value = None
    mock_client_instance.list_threads.return_value = mock_threads_list
    mock_client_instance.get_thread.return_value = mock_thread_details
    # Mock get_attachment to return some bytes
    mock_client_instance.get_attachment.return_value = b"fake_attachment_content"
    
    # 4. Patch GmailClient to return our mock instance
    # We must patch where it is DEFINED or IMPORTED.
    # It is defined in core.ingestion.gmail_client.GmailClient
    # And used inside email_fetcher._fetch_gmail_threads
    with patch('core.ingestion.gmail_client.GmailClient', return_value=mock_client_instance):
        
        # 5. Initialize Service
        service = IngestionService(db=mock_db)
        
        # 6. Run Sync (Mock User)
        user = User(
            id="user-1", 
            email="user@example.com", 
            provider=EmailProvider.GMAIL,
            access_token="fake-token"
        )
        
        # Mock Connected Account
        from models.connected_account import ConnectedAccount, ProviderType
        mock_account = ConnectedAccount(
            id="acc-1",
            user_id=user.id,
            provider=ProviderType.GMAIL,
            access_token="fake-token"
        )
        
        # Setup DB Mock to return connected account
        # db.execute(stmt) returns a Result object (mock_result)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_account]
        mock_db.execute.return_value = mock_result
        
        # Patch _store_attachment
        with patch('core.ingestion.attachment_extractor._store_attachment', new_callable=AsyncMock) as mock_store_attachment:
            mock_store_attachment.return_value = "/tmp/fake_path.pdf"
            
            await service.sync_user_emails(user.id)
            
            print("Sync completed without error.")
            
            # 7. Verification Steps
            
            # Verify _store_attachment called
            if mock_store_attachment.called:
                print(f"Attachment Stored. Call count: {mock_store_attachment.call_count}")
            else:
                print("Attachment Storage NOT called.")
                
            assert mock_store_attachment.called
        
        # Verify DB Calls (Threads Upserted)
        # We can inspect the calls to mock_db.add (IngestionService uses add/flush for Messages)
        
        message_saved = False
        sanitization_successful = False
        
        for call in mock_db.add.call_args_list:
            arg = call[0][0] # First arg of call
            if isinstance(arg, Email):
                message_saved = True
                print(f"Inspecting Saved Email Body: {arg.body_plain}")
                
                # Check Sanitization
                if "<script>" not in arg.body_plain and "<h1>Safe Title</h1>" in arg.body_plain:
                     sanitization_successful = True
                     print("Sanitization Verified: Script tag removed.")
                else:
                     print("Sanitization Failed! Script tag present.")
                     
        if not message_saved:
            print("No Email object saved to DB.")

        assert message_saved
        assert sanitization_successful

if __name__ == "__main__":
    asyncio.run(verify_ingestion_flow())
