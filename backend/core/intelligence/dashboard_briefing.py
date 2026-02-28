"""
Dashboard AI Briefing
---------------------
Creates a lightning-fast aggregated view of all high priority/high urgency 
AI discoveries across the user's inbox without requiring a new LLM call.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timezone

from models.thread import Thread

logger = logging.getLogger(__name__)

async def get_dashboard_briefing(user_id: str, db: AsyncSession, min_urgency: int = 70) -> Dict[str, Any]:
    """
    Aggregates existing Thread intelligence (where urgency >= min_urgency) 
    into a structured briefing for the dashboard.
    """
    try:
        # Fetch high urgency threads that haven't been archived/deleted
        stmt = select(Thread).where(
            Thread.user_id == user_id,
            Thread.urgency_score >= min_urgency,
            Thread.is_archived == False,
            Thread.is_trash == False
        ).order_by(desc(Thread.urgency_score)).limit(10)
        
        result = await db.execute(stmt)
        critical_threads = result.scalars().all()
        
        briefing_items = []
        total_urgent_actions = 0
        
        for t in critical_threads:
            # Safely parse cached intel
            intel = t.intel_json or {}
            action_items = intel.get("action_items", [])
            total_urgent_actions += len(action_items)
            
            briefing_items.append({
                "thread_id": t.id,
                "subject": t.subject,
                "summary": t.summary,
                "urgency_score": t.urgency_score,
                "intent": t.intent,
                "action_items": action_items,
                "generated_at": t.intel_generated_at.isoformat() if t.intel_generated_at else datetime.now(timezone.utc).isoformat()
            })
            
        # Overall status synthesis (static logic for speed)
        overall_status = "clear"
        if len(critical_threads) > 5 or total_urgent_actions > 10:
            overall_status = "overwhelmed"
        elif len(critical_threads) > 0:
            overall_status = "action_required"
            
        return {
            "status": overall_status,
            "critical_threads_count": len(critical_threads),
            "total_action_items": total_urgent_actions,
            "briefing_items": briefing_items
        }
        
    except Exception as e:
        logger.error(f"Failed to generate dashboard briefing: {e}")
        return {
            "status": "error",
            "critical_threads_count": 0,
            "total_action_items": 0,
            "briefing_items": []
        }
