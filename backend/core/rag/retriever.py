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
    Filters by user_id to ensure strict tenant isolation — one user NEVER sees another's data.
    """
    try:
        # Generate the embedding query vector
        query_embedding = await generate_embedding(
            query_text,
            user_id=user_id,
            operation_type="rag_query_embedding",
            related_entity_type="search",
            related_entity_id=None,
            metadata={"source_type": "rag_query"},
        )

        # Strict where filter — enforces user-level tenant isolation
        where_filter = {"user_id": str(user_id)}

        # Call query() which mandates user_id in where
        results = await vector_store.query(
            query_embeddings=[query_embedding],
            n_results=limit * 2,  # Fetch extra to allow filtering out excluded source
            where=where_filter
        )

        # Format the results
        formatted_results = []
        if not results or not results.get('ids') or len(results['ids']) == 0:
            return formatted_results

        ids = results['ids'][0] if results['ids'] else []
        distances = results['distances'][0] if results.get('distances') else [0.0] * len(ids)
        documents = results['documents'][0] if results.get('documents') else [""] * len(ids)
        metadatas = results['metadatas'][0] if results.get('metadatas') else [{}] * len(ids)

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
