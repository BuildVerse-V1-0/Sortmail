"""
File Storage
------------
Cloud/local file storage for attachments.
"""

import os
import aiofiles
from typing import Optional
from app.config import settings


class FileStorage:
    """File storage abstraction."""
    
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)
    
    async def save(
        self,
        file_id: str,
        filename: str,
        content: bytes,
    ) -> str:
        """
        Save a file and return storage path.
        """
        safe_filename = f"{file_id}_{filename}"
        full_path = os.path.join(self.storage_path, safe_filename)
        
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)
        
        return full_path
    
    async def get(self, path: str) -> Optional[bytes]:
        """Read a file from storage."""
        if not os.path.exists(path):
            return None
        
        async with aiofiles.open(path, "rb") as f:
            return await f.read()
    
    async def delete(self, path: str) -> bool:
        """Delete a file."""
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
    
    def get_url(self, path: str) -> str:
        """Get a URL for a stored file."""
        # In production, return cloud storage URL
        return f"/files/{os.path.basename(path)}"


# Singleton instance
file_storage = FileStorage()
