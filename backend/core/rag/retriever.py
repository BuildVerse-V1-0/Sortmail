"""
RAG Retriever
-------------
Searches the ChromaDB vector store for semantically similar items (threads, attachments).
"""

import logging
from typing import List, Dict, Any

from core.storage.vector_store import vector_store
from core.rag.embeddings import generate_embedding

logger = logging.getLogger(__name__)

async def get_similar_context(query_text: str, user_id: str, limit: int = 5, exclude_source_id: str = None) -> List[Dict[str, Any]]:
    """
    Finds semantically similar context items (threads or attachments) from ChromaDB.
    Filters by user_id to ensure tenant isolation.
    """
    try:
        # Generate the embedding query vector
        query_embedding = await generate_embedding(query_text)
        
        # Build strict where filter for multi-tenant isolation
        where_filter = {"user_id": user_id}
        
        # Query the underlying Chroma DB collection via our async wrapper
        # The Wrapper expects querying by embedding
        results = await vector_store.query(
            query_embeddings=[query_embedding],
            n_results=limit * 2,  # Fetch extra to filter out the excluded source ID manually if needed
            where=where_filter
        )
        
        # Format the results
        formatted_results = []
        if not results or not results['ids'] or len(results['ids']) == 0:
            return formatted_results
            
        ids = results['ids'][0]
        distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0] * len(ids)
        documents = results['documents'][0] if 'documents' in results and results['documents'] else [""] * len(ids)
        metadatas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(ids)
        
        for i in range(len(ids)):
            meta = metadatas[i] or {}
            source_id = meta.get("source_id")
            
            # Avoid self-referencing context
            if exclude_source_id and source_id == exclude_source_id:
                continue
                
            formatted_results.append({
                "id": ids[i],
                "distance": distances[i],
                "document": documents[i],
                "metadata": meta,
                "source_type": meta.get("source_type"),
                "source_id": source_id,
            })
            
            if len(formatted_results) >= limit:
                break
                
        return formatted_results
        
    except Exception as e:
        logger.error(f"Failed to retrieve similar context: {e}")
        return []
