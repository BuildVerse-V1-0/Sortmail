"""
S3 / R2 Cold Storage Strategy
-----------------------------
Handles compressed text and raw attachments in Tier 3 storage.
"""
import logging
import gzip
import asyncio
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        self.client = None
        self.bucket_name = settings.S3_BUCKET_NAME
        
        if self.bucket_name and settings.AWS_ACCESS_KEY_ID:
            try:
                # boto3 takes kwargs, endpoint_url enables Cloudflare R2
                kwargs = {
                    'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                    'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
                    'region_name': settings.AWS_REGION_NAME,
                }
                if settings.S3_ENDPOINT_URL:
                    kwargs['endpoint_url'] = settings.S3_ENDPOINT_URL
                    
                self.client = boto3.client('s3', **kwargs)
                logger.info(f"S3/R2 Client initialized for bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 wrapper: {e}")

    async def upload_compressed(self, content: str, s3_path: str) -> Optional[str]:
        """Compress string content and upload to specific S3 path."""
        if not self.client:
             logger.warning("S3 client not initialized. Local fallback not yet implemented.")
             return None
             
        try:
             compressed_bytes = gzip.compress(content.encode('utf-8'))
             # Run synchronous boto3 block in threadpool executor to avoid blocking the event loop
             await asyncio.to_thread(
                 self.client.put_object,
                 Bucket=self.bucket_name,
                 Key=s3_path,
                 Body=compressed_bytes,
                 ContentType='application/gzip'
             )
             return s3_path
        except ClientError as e:
             logger.error(f"S3 upload error for {s3_path}: {e}")
             return None

    async def download_decompressed(self, s3_path: str) -> Optional[str]:
        """Download compressed file and decode to string."""
        if not self.client:
             return None
             
        try:
             response = await asyncio.to_thread(
                 self.client.get_object,
                 Bucket=self.bucket_name,
                 Key=s3_path
             )
             
             # Read the stream synchronously in a thread
             compressed_bytes = await asyncio.to_thread(response['Body'].read)
             return gzip.decompress(compressed_bytes).decode('utf-8')
             
        except ClientError as e:
             logger.error(f"S3 download error for {s3_path}: {e}")
             return None

# Singleton Interface
s3_client = S3Storage()
