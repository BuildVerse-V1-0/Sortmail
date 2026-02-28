"""
Shared Embeddings Module
------------------------
Provides LLM-agnostic embedding generation for RAG pipelines.
"""

import logging
import asyncio
from typing import List, Dict

logger = logging.getLogger(__name__)

def _estimate_tokens(text: str) -> int:
    """Estimate token count for routing constraints."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Fallback estimation 1 token ~= 1.3 words (standard cl100k estimate)
        return int(len(text.split()) * 1.3)

async def generate_embedding(text: str) -> List[float]:
    """Generate generic embedding using configured LLM Provider (Gemini/OpenAI)."""
    from app.config import settings
    
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Using Google's text-embedding model in a threadpool
        def _embed():
            return genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
        try:    
            result = await asyncio.to_thread(_embed)
            return result['embedding']
        except Exception as e:
            logger.error(f"Failed embedding generation via Gemini: {e}")
            return [0.0] * 768
            
    elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed embedding generation via OpenAI: {e}")
            return [0.0] * 1536
            
    # Dev mock fallback if APIs unconfigured
    return [0.0] * 768

def chunk_text_for_rag(text: str, max_chunk_tokens: int = 512) -> List[Dict]:
    """Smart chunking that preserves meaning based on paragraph boundaries."""
    paragraphs = text.split('\\n\\n')
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = _estimate_tokens(para)
        
        if para_tokens > max_chunk_tokens:
            sentences = para.split('. ')
            for sentence in sentences:
                sent_tokens = _estimate_tokens(sentence)
                if current_tokens + sent_tokens > max_chunk_tokens:
                    if current_chunk:
                        chunks.append({
                            'text': current_chunk.strip(),
                            'tokens': current_tokens
                        })
                    current_chunk = sentence + '. '
                    current_tokens = sent_tokens
                else:
                    current_chunk += sentence + '. '
                    current_tokens += sent_tokens
        else:
            if current_tokens + para_tokens > max_chunk_tokens:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'tokens': current_tokens
                    })
                current_chunk = para + '\\n\\n'
                current_tokens = para_tokens
            else:
                current_chunk += para + '\\n\\n'
                current_tokens += para_tokens
                
    if current_chunk:
        chunks.append({
            'text': current_chunk.strip(),
            'tokens': current_tokens
        })
        
    return chunks
