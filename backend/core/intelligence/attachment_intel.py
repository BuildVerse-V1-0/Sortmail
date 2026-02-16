"""
Attachment Intelligence
-----------------------
Analyzes document attachments and produces AttachmentIntel.

Note: AttachmentIntel is an INTERNAL type, embedded in ThreadIntelV1.
"""

from typing import List

from contracts import AttachmentRef, AttachmentIntel
from app.config import settings


async def analyze_attachments(
    attachments: List[AttachmentRef],
    model: str = "gemini-1.5-pro",
) -> List[AttachmentIntel]:
    """
    Analyze all attachments and produce intelligence.
    
    Args:
        attachments: List of attachment references
        model: LLM model to use
        
    Returns:
        List of AttachmentIntel (embedded in ThreadIntelV1)
    """
    results = []
    
    for att in attachments:
        intel = await _analyze_single_attachment(att, model)
        if intel:
            results.append(intel)
    
    return results


async def _analyze_single_attachment(
    attachment: AttachmentRef,
    model: str,
) -> AttachmentIntel:
    """Analyze a single attachment."""
    # Extract text based on type
    text = await _extract_text(attachment)
    
    if not text:
        return AttachmentIntel(
            attachment_id=attachment.attachment_id,
            summary="Could not extract text from document",
            key_points=[],
            document_type="unknown",
            importance="low",
        )
    
    # Generate summary with LLM
    summary = await _summarize_document(text, model)
    key_points = await _extract_key_points(text, model)
    doc_type = _classify_document_type(attachment, text)
    importance = _assess_importance(doc_type, key_points)
    
    return AttachmentIntel(
        attachment_id=attachment.attachment_id,
        summary=summary,
        key_points=key_points,
        document_type=doc_type,
        importance=importance,
    )


async def _extract_text(attachment: AttachmentRef) -> str:
    """Extract text from attachment file."""
    if not attachment.storage_path:
        return ""
    
    try:
        if attachment.mime_type == "application/pdf":
            return _extract_pdf_text(attachment.storage_path)
        elif "word" in attachment.mime_type or attachment.mime_type.endswith(".document"):
            return _extract_docx_text(attachment.storage_path)
        elif "powerpoint" in attachment.mime_type or attachment.mime_type.endswith(".presentation"):
            return _extract_pptx_text(attachment.storage_path)
        else:
            return ""
    except Exception:
        return ""


def _extract_pdf_text(path: str) -> str:
    """Extract text from PDF."""
    # TODO: Implement with pypdf
    # from pypdf import PdfReader
    # reader = PdfReader(path)
    # text = ""
    # for page in reader.pages:
    #     text += page.extract_text()
    # return text
    return ""


def _extract_docx_text(path: str) -> str:
    """Extract text from DOCX."""
    # TODO: Implement with python-docx
    # from docx import Document
    # doc = Document(path)
    # return "\n".join(p.text for p in doc.paragraphs)
    return ""


def _extract_pptx_text(path: str) -> str:
    """Extract text from PPTX."""
    # TODO: Implement with python-pptx
    # from pptx import Presentation
    # prs = Presentation(path)
    # text = ""
    # for slide in prs.slides:
    #     for shape in slide.shapes:
    #         if hasattr(shape, "text"):
    #             text += shape.text + "\n"
    # return text
    return ""


async def _summarize_document(text: str, model: str) -> str:
    """Generate document summary with LLM."""
    # TODO: Implement LLM summarization
    return f"Document summary (first 100 chars): {text[:100]}..."


async def _extract_key_points(text: str, model: str) -> List[str]:
    """Extract key points from document."""
    # TODO: Implement LLM key point extraction
    return ["Key point 1", "Key point 2"]


def _classify_document_type(attachment: AttachmentRef, text: str) -> str:
    """Classify document type based on content."""
    filename_lower = attachment.filename.lower()
    text_lower = text.lower()
    
    if "contract" in filename_lower or "agreement" in text_lower:
        return "contract"
    elif "invoice" in filename_lower or "total due" in text_lower:
        return "invoice"
    elif "proposal" in filename_lower or "we propose" in text_lower:
        return "proposal"
    elif "resume" in filename_lower or "cv" in filename_lower:
        return "resume"
    elif "report" in filename_lower:
        return "report"
    else:
        return "document"


def _assess_importance(doc_type: str, key_points: List[str]) -> str:
    """Assess document importance."""
    high_importance_types = ["contract", "invoice", "proposal"]
    if doc_type in high_importance_types:
        return "high"
    elif len(key_points) >= 3:
        return "medium"
    else:
        return "low"
