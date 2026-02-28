"""
Attachment Context Strategy
---------------------------
Implements the multi-tier Hybrid RAG Storage logic for processing large emails and attachments.
Routes to PostgreSQL, ChromaDB, and S3 Storage based on the document's token volume.
"""

from core.rag.embeddings import generate_embedding, chunk_text_for_rag, _estimate_tokens

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
            embedding = await generate_embedding(chunk['text'])
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
            embedding = await generate_embedding(chunk['text'])
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
        embedding = await generate_embedding(summary_text)
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
