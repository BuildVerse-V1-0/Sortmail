"""
Vector Store Client
-------------------
Chroma vector database for Tier 2 Semantic Search.
"""

from typing import List, Optional
import logging
from app.config import settings
import asyncio

logger = logging.getLogger(__name__)

class VectorStore:
    """Chroma vector store wrapper for email and attachment context."""
    
    def __init__(self):
        self._client = None
        self._collection = None
        
    async def initialize(self):
        """Initialize Chroma client."""
        try:
            import chromadb
            
            # Initialize synchronously in a thread
            def _init_chroma():
                client = chromadb.CloudClient(
                    api_key=settings.CHROMA_API_KEY,
                    tenant=settings.CHROMA_TENANT,
                    database=settings.CHROMA_DATABASE
                )
                return client, client.get_or_create_collection(name="my_collection")
                
            self._client, self._collection = await asyncio.to_thread(_init_chroma)
            logger.info("ChromaDB Cloud Client initialized.")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chroma Cloud DB: {e}")
    
    async def add(
        self,
        id: str,
        document: str,
        embedding: List[float],
        metadata: dict,
    ):
        """Add a document with its pre-computed embedding to the vector store."""
        if not self._collection:
            logger.warning("Chroma collection not initialized.")
            return
            
        try:
            def _add():
                self._collection.add(
                    ids=[id],
                    documents=[document],
                    embeddings=[embedding],
                    metadatas=[metadata],
                )
            await asyncio.to_thread(_add)
        except Exception as e:
            logger.error(f"Failed to add embedding to Chroma: {e}")
            
    async def add_batch(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ):
        """Add multiple documents efficiently."""
        if not self._collection:
            return
            
        try:
            def _add_batch():
                self._collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
            await asyncio.to_thread(_add_batch)
        except Exception as e:
            logger.error(f"Failed to batch add to Chroma: {e}")
    
    async def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where_filter: Optional[dict] = None,
    ) -> dict:
        """Search for semantically similar documents based on strict metadata constraints."""
        if not self._collection:
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
            
        try:
            def _search():
                return self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where_filter,
                    include=['documents', 'metadatas', 'distances']
                )
            return await asyncio.to_thread(_search)
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    async def delete(self, id: str):
        """Delete a document."""
        if not self._collection:
            return
        try:
            def _delete():
                self._collection.delete(ids=[id])
            await asyncio.to_thread(_delete)
        except Exception as e:
            logger.error(f"Failed to delete from Chroma: {e}")

# Singleton instance for internal python usage
vector_store = VectorStore()

# ─────────────────────────────────────────────────────────────────────────
# FastAPI Dependency Injection
# ─────────────────────────────────────────────────────────────────────────
from fastapi import Depends
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

_fastapi_client: ClientAPI | None = None
_fastapi_collection: Collection | None = None

def get_chroma_client() -> ClientAPI:
    """Get the raw Chroma Cloud Client synchronously for FastAPI Routes."""
    global _fastapi_client
    if _fastapi_client is None:
        import chromadb
        _fastapi_client = chromadb.CloudClient(
            api_key=settings.CHROMA_API_KEY,
            tenant=settings.CHROMA_TENANT,
            database=settings.CHROMA_DATABASE
        )
    return _fastapi_client

def get_chroma_collection(client: ClientAPI = Depends(get_chroma_client)) -> Collection:
    """Get the target collection synchronously for FastAPI Routes."""
    global _fastapi_collection
    if _fastapi_collection is None:
        _fastapi_collection = client.get_or_create_collection(
            name="my_collection",
        )
    return _fastapi_collection
