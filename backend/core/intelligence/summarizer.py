"""
Thread Summarizer
-----------------
Uses LLM to generate executive summaries of email threads.
"""

from typing import Optional
from contracts import EmailThreadV1

from app.config import settings


async def summarize_thread(
    thread: EmailThreadV1,
    model: str = "gemini-1.5-pro",
) -> str:
    """
    Generate an executive summary of an email thread.
    
    Args:
        thread: EmailThreadV1 to summarize
        model: LLM model to use
        
    Returns:
        2-3 sentence executive summary
    """
    # Build context from thread
    context = _build_thread_context(thread)
    
    # Generate summary with LLM
    summary = await _generate_summary(context, model)
    
    return summary


def _build_thread_context(thread: EmailThreadV1) -> str:
    """Build context string for LLM prompt."""
    messages_text = []
    
    for msg in thread.messages:
        sender = "You" if msg.is_from_user else msg.from_address
        messages_text.append(f"From: {sender}\n{msg.body_text[:500]}")
    
    return f"""
Subject: {thread.subject}
Participants: {', '.join(thread.participants)}

Messages:
{chr(10).join(messages_text)}

Attachments: {len(thread.attachments)} files
"""


async def _generate_summary(context: str, model: str) -> str:
    """Call LLM to generate summary."""
    prompt = f"""Summarize this email thread in 2-3 sentences. Focus on:
- What is the main topic?
- What action is needed (if any)?
- What is the deadline (if any)?

Thread:
{context}

Summary:"""
    
    if settings.LLM_PROVIDER == "gemini":
        return await _call_gemini(prompt, model)
    elif settings.LLM_PROVIDER == "openai":
        return await _call_openai(prompt, model)
    else:
        # Fallback for testing
        return f"Summary of thread: {context[:100]}..."


async def _call_gemini(prompt: str, model: str) -> str:
    """Call Google Gemini API."""
    # TODO: Implement Gemini API call
    # import google.generativeai as genai
    # genai.configure(api_key=settings.GEMINI_API_KEY)
    # model = genai.GenerativeModel(model)
    # response = model.generate_content(prompt)
    # return response.text
    raise NotImplementedError("Implement Gemini API call")


async def _call_openai(prompt: str, model: str) -> str:
    """Call OpenAI API."""
    # TODO: Implement OpenAI API call
    # from openai import OpenAI
    # client = OpenAI(api_key=settings.OPENAI_API_KEY)
    # response = client.chat.completions.create(...)
    # return response.choices[0].message.content
    raise NotImplementedError("Implement OpenAI API call")
