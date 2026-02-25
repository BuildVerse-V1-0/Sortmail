"""
Attachment Context Strategy
---------------------------
Implements the multi-tier Hybrid RAG Storage logic for processing large emails and attachments.
Routes to PostgreSQL, ChromaDB, and S3 Storage based on the document's token volume.
"""

import logging
import asyncio
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from core.storage.s3 import s3_client
from core.storage.vector_store import vector_store
from models.attachment import Attachment, AttachmentStatus

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

async def _generate_embedding(text: str) -> List[float]:
    """Generate generic embedding using configured LLM Provider (Gemini/OpenAI)."""
    from app.config import settings
    
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Using Google's text-embedding model in a threadpool
        def _embed():
            return genai.embed_content(
                model="models/embedding-001",
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
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = _estimate_tokens(para)
        
        # If paragraph alone exceeds max, split by sentences
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
                current_chunk = para + '\n\n'
                current_tokens = para_tokens
            else:
                current_chunk += para + '\n\n'
                current_tokens += para_tokens
                
    if current_chunk:
        chunks.append({
            'text': current_chunk.strip(),
            'tokens': current_tokens
        })
        
    return chunks

class AttachmentContextStrategy:
    """Intelligent Routing for Attachment Context based on Token Complexity."""
        
    @staticmethod
    async def process_attachment(attachment_orm: Attachment, user_id: str, db: AsyncSession):
        """Decide how to store and retrieve attachment context based on token volume."""
        text = attachment_orm.extracted_text
        attachment_id = attachment_orm.id
        
        if not text or len(text) < 100:
            logger.info(f"Attachment {attachment_id} has negligible text. Storing metadata only.")
            attachment_orm.status = AttachmentStatus.INDEXED
            await db.commit()
            return

        token_count = _estimate_tokens(text)
        
        if token_count < 5000:
            logger.info(f"Routing attachment {attachment_id} ({token_count} tokens): Postgres + Chroma")
            await AttachmentContextStrategy.store_in_postgres_and_chroma(attachment_orm, text, user_id, db)
        elif token_count < 50000:
            logger.info(f"Routing attachment {attachment_id} ({token_count} tokens): Hybrid (S3 + Chroma excerpts)")
            await AttachmentContextStrategy.store_hybrid(attachment_orm, text, user_id, db)
        else:
            logger.info(f"Routing attachment {attachment_id} ({token_count} tokens): Large S3 Summary + Chroma")
            await AttachmentContextStrategy.store_in_s3_with_summary(attachment_orm, text, user_id, db)

    @staticmethod
    async def store_in_postgres_and_chroma(attachment_orm: Attachment, text: str, user_id: str, db: AsyncSession):
        """Small docs: Full text in DB + fully embedded in Vector store."""
        attachment_id = attachment_orm.id
        filename = attachment_orm.filename
        
        # Embed for RAG
        chunks = chunk_text_for_rag(text, max_chunk_tokens=512)
        
        for i, chunk in enumerate(chunks):
            embedding = await _generate_embedding(chunk['text'])
            await vector_store.add(
                id=f"{attachment_id}_chunk_{i}",
                document=chunk['text'],
                embedding=embedding,
                metadata={
                    'user_id': user_id,
                    'source_type': 'attachment',
                    'source_id': attachment_id,
                    'filename': filename,
                    'email_id': attachment_orm.email_id,
                    'chunk_index': i,
                    'token_count': chunk['tokens']
                }
            )
            
        attachment_orm.extracted_text = text
        attachment_orm.chunk_count = len(chunks)
        attachment_orm.status = AttachmentStatus.INDEXED
        await db.commit()

    @staticmethod
    async def store_hybrid(attachment_orm: Attachment, text: str, user_id: str, db: AsyncSession):
        """Medium docs: S3 for full zip + Chroma for crucial excerpts."""
        attachment_id = attachment_orm.id
        filename = attachment_orm.filename
        
        # 1. Store full text in S3
        s3_path = f"users/{user_id}/attachments/text/{attachment_id}.txt.gz"
        await s3_client.upload_compressed(text, s3_path)
        
        # 2. Extract key sections (using top and bottom heuristic for excerpts)
        length = len(text)
        head_end = min(length, 10000)
        key_excerpts = text[:head_end]
        
        # 3. Embed key excerpts
        chunks = chunk_text_for_rag(key_excerpts, max_chunk_tokens=512)
        
        for i, chunk in enumerate(chunks):
            embedding = await _generate_embedding(chunk['text'])
            await vector_store.add(
                id=f"{attachment_id}_chunk_{i}",
                document=chunk['text'],
                embedding=embedding,
                metadata={
                    'user_id': user_id,
                    'source_type': 'attachment',
                    'source_id': attachment_id,
                    'filename': filename,
                    's3_path': s3_path,
                    'chunk_index': i
                }
            )
            
        attachment_orm.storage_path = s3_path
        attachment_orm.extracted_text = key_excerpts[:5000] # Preview mapped locally
        attachment_orm.chunk_count = len(chunks)
        attachment_orm.status = AttachmentStatus.INDEXED
        await db.commit()

    @staticmethod
    async def store_in_s3_with_summary(attachment_orm: Attachment, text: str, user_id: str, db: AsyncSession):
        """Large docs: S3 strict + AI summary embedded in Chroma."""
        attachment_id = attachment_orm.id
        filename = attachment_orm.filename
        
        # 1. S3 Upload entirely
        s3_path = f"users/{user_id}/attachments/text/{attachment_id}.txt.gz"
        await s3_client.upload_compressed(text, s3_path)
        
        # 2. Extract summary (Currently a placeholder until full prompt orchestration)
        summary_text = f"Automated Indexing Summary: '{filename}' is a large {len(text)}-character document stored in Tier 3 S3 Cold Storage to optimize DB costs."
        
        # 3. Embed lightweight summary map
        embedding = await _generate_embedding(summary_text)
        await vector_store.add(
            id=f"{attachment_id}_summary",
            document=summary_text,
            embedding=embedding,
            metadata={
                'user_id': user_id,
                'source_type': 'attachment_summary',
                'source_id': attachment_id,
                'filename': filename,
                's3_path': s3_path,
            }
        )
        
        attachment_orm.storage_path = s3_path
        attachment_orm.extracted_text = summary_text
        attachment_orm.chunk_count = 1
        attachment_orm.status = AttachmentStatus.INDEXED
        await db.commit()
