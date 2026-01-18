# Intelligence Module
from .email_intel import analyze_thread
from .summarizer import summarize_thread
from .intent_classifier import classify_intent
from .deadline_extractor import extract_deadlines
from .entity_extractor import extract_entities
from .attachment_intel import analyze_attachments

__all__ = [
    "analyze_thread",
    "summarize_thread",
    "classify_intent",
    "extract_deadlines",
    "extract_entities",
    "analyze_attachments",
]
