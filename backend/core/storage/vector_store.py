"""
Vector Store Client
-------------------
Chroma vector database for Tier 2 Semantic Search.
"""

from typing import List, Optional
import logging
import hashlib
from app.config import settings
import asyncio

logger = logging.getLogger(__name__)

MAX_VECTOR_ID_BYTES = 120


def _normalize_vector_id(raw_id: str) -> str:
    """Keep vector IDs under provider byte limits using deterministic hashing."""
    if len(raw_id.encode("utf-8")) <= MAX_VECTOR_ID_BYTES:
        return raw_id
    digest = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:40]
    return f"vid_{digest}"

class VectorStore:
    """Chroma vector store wrapper for email and attachment context."""
    
    def __init__(self):
        self._client = None
        self._collection = None
        
    async def initialize(self):
        """Initialize Chroma client."""
        if not settings.CHROMA_API_KEY or not settings.CHROMA_TENANT or not settings.CHROMA_DATABASE:
            logger.warning("ChromaDB not configured (missing CHROMA_API_KEY/CHROMA_TENANT/CHROMA_DATABASE). Skipping vector store init.")
            return
            
        try:
            import chromadb
            
            # Diagnostic log — helps confirm env vars are loaded correctly on Railway
            key_preview = settings.CHROMA_API_KEY[:8] + "..." if settings.CHROMA_API_KEY else "MISSING"
            logger.info(f"Connecting to ChromaDB Cloud: tenant={settings.CHROMA_TENANT} db={settings.CHROMA_DATABASE} key={key_preview}")

            
            # Initialize synchronously in a thread
            def _init_chroma():
                client = chromadb.CloudClient(
                    api_key=settings.CHROMA_API_KEY,
                    tenant=settings.CHROMA_TENANT,
                    database=settings.CHROMA_DATABASE
                )
                return client, client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)
                
            self._client, self._collection = await asyncio.to_thread(_init_chroma)
            logger.info("ChromaDB Cloud Client initialized successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Chroma Cloud DB: {e}")
            return False
    
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
            normalized_id = _normalize_vector_id(id)
            metadata_safe = dict(metadata or {})
            if "user_id" in metadata_safe and metadata_safe["user_id"] is not None:
                metadata_safe["user_id"] = str(metadata_safe["user_id"])
            if normalized_id != id:
                metadata_safe.setdefault("vector_original_id", id)

            def _add():
                self._collection.add(
                    ids=[normalized_id],
                    documents=[document],
                    embeddings=[embedding],
                    metadatas=[metadata_safe],
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
            normalized_ids = []
            normalized_metadatas = []
            for i, raw_id in enumerate(ids):
                normalized_id = _normalize_vector_id(raw_id)
                metadata_safe = dict((metadatas[i] if i < len(metadatas) else {}) or {})
                if "user_id" in metadata_safe and metadata_safe["user_id"] is not None:
                    metadata_safe["user_id"] = str(metadata_safe["user_id"])
                if normalized_id != raw_id:
                    metadata_safe.setdefault("vector_original_id", raw_id)
                normalized_ids.append(normalized_id)
                normalized_metadatas.append(metadata_safe)

            def _add_batch():
                self._collection.add(
                    ids=normalized_ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=normalized_metadatas,
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
    
    async def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[dict] = None,
        include: Optional[List[str]] = None,
    ) -> dict:
        """Query the collection using Chroma's native API (query_embeddings list).
        Always requires a 'where' filter to enforce user-level tenant isolation.
        """
        if not self._collection:
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

        if not where or "user_id" not in where:
            logger.error("ChromaDB query attempted WITHOUT user_id filter — blocked for security.")
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

        try:
            def _query():
                return self._collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where=where,
                    include=include or ['documents', 'metadatas', 'distances']
                )
            return await asyncio.to_thread(_query)
        except Exception as e:
            logger.error(f"ChromaDB query failed: {e}")
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

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
            name=settings.CHROMA_COLLECTION_NAME,
        )
    return _fastapi_collection
