"""
API Routes - Notifications
--------------------------
In-app notification endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from pydantic import BaseModel
from datetime import datetime, timezone

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from models.notification import Notification

router = APIRouter()


class NotificationOut(BaseModel):
    id: str
    type: str
    title: str
    body: Optional[str]
    action_url: Optional[str]
    is_read: bool
    priority: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[NotificationOut])
async def list_notifications(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List recent notifications for the current user."""
    stmt = (
        select(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.is_dismissed == False,
        )
        .order_by(desc(Notification.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    return notifications


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    stmt = (
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    await db.execute(stmt)
    await db.commit()
    return {"success": True}


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    await db.execute(stmt)
    await db.commit()
    return {"success": True}


@router.delete("/{notification_id}")
async def dismiss_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dismiss (soft-delete) a notification."""
    stmt = (
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .values(is_dismissed=True, dismissed_at=datetime.now(timezone.utc))
    )
    await db.execute(stmt)
    await db.commit()
    return {"success": True}


# ─── Notification Preferences ──────────────────────────────────────────────────

from models.notification import NotificationPreferences
import uuid as _uuid


class NotificationPreferencesOut(BaseModel):
    email_enabled: bool
    push_enabled: bool
    in_app_enabled: bool
    channels: dict
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    quiet_hours_timezone: Optional[str]

    class Config:
        from_attributes = True


class UpdateNotificationPreferencesRequest(BaseModel):
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    channels: Optional[dict] = None
    quiet_hours_start: Optional[str] = None   # "22:00"
    quiet_hours_end: Optional[str] = None     # "08:00"
    quiet_hours_timezone: Optional[str] = None


@router.get("/preferences", response_model=NotificationPreferencesOut)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's notification preferences."""
    stmt = select(NotificationPreferences).where(
        NotificationPreferences.user_id == current_user.id
    )
    result = await db.execute(stmt)
    prefs = result.scalar_one_or_none()

    if not prefs:
        # Create defaults
        prefs = NotificationPreferences(
            id=str(_uuid.uuid4()),
            user_id=current_user.id,
        )
        db.add(prefs)
        try:
            await db.commit()
        except Exception:
            # Handle parallel TOCTOU initialization race
            await db.rollback()
            result = await db.execute(stmt)
            prefs = result.scalar_one_or_none()
            if not prefs: raise

    return NotificationPreferencesOut(
        email_enabled=prefs.email_enabled,
        push_enabled=prefs.push_enabled,
        in_app_enabled=prefs.in_app_enabled,
        channels=prefs.channels or {},
        quiet_hours_start=prefs.quiet_hours_start.strftime("%H:%M") if prefs.quiet_hours_start else None,
        quiet_hours_end=prefs.quiet_hours_end.strftime("%H:%M") if prefs.quiet_hours_end else None,
        quiet_hours_timezone=prefs.quiet_hours_timezone,
    )


@router.patch("/preferences")
async def update_notification_preferences(
    body: UpdateNotificationPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's notification preferences."""
    from datetime import time as dtime
    stmt = select(NotificationPreferences).where(
        NotificationPreferences.user_id == current_user.id
    )
    result = await db.execute(stmt)
    prefs = result.scalar_one_or_none()

    if not prefs:
        prefs = NotificationPreferences(
            id=str(_uuid.uuid4()),
            user_id=current_user.id,
        )
        db.add(prefs)

    if body.email_enabled is not None:
        prefs.email_enabled = body.email_enabled
    if body.push_enabled is not None:
        prefs.push_enabled = body.push_enabled
    if body.in_app_enabled is not None:
        prefs.in_app_enabled = body.in_app_enabled
    if body.channels is not None:
        prefs.channels = body.channels
    try:
        if body.quiet_hours_start is not None:
            h, m = map(int, body.quiet_hours_start.split(":"))
            prefs.quiet_hours_start = dtime(h, m)
        if body.quiet_hours_end is not None:
            h, m = map(int, body.quiet_hours_end.split(":"))
            prefs.quiet_hours_end = dtime(h, m)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Expected HH:MM")

    if body.quiet_hours_timezone is not None:
        prefs.quiet_hours_timezone = body.quiet_hours_timezone

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update preferences")
    return {"updated": True}
