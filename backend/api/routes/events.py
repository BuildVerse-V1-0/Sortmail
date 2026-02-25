"""
API Routes - Server-Sent Events
---------------------------------
Real-time push to frontend: new_emails, intel_ready, sync_status.

Frontend subscribes once per session:
    const es = new EventSource('/api/events/stream', { withCredentials: true })
    es.onmessage = (e) => { ... }
"""

import asyncio
import json
import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from api.dependencies import get_current_user
from models.user import User
from core.redis import get_redis

router = APIRouter()
logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 25  # seconds — keeps connection alive through proxies


@router.get("/stream")
async def event_stream(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    SSE stream for real-time inbox updates.

    Events emitted:
    - heartbeat      : keep-alive every 25s
    - new_emails     : N new threads arrived after incremental sync
    - intel_ready    : AI analysis complete for a thread
    - sync_status    : Sync started / finished

    Frontend usage:
        const es = new EventSource('/api/events/stream', { withCredentials: true })
        es.addEventListener('intel_ready', (e) => {
            const { thread_id, summary, urgency_score } = JSON.parse(e.data)
            queryClient.invalidateQueries(['threads'])
        })
    """
    user_id = str(current_user.id)
    channel = f"user:{user_id}:events"

    async def generator():
        try:
            r = await get_redis()
        except Exception:
            r = None

        if r:
            # Subscribe to Redis pub/sub channel
            pubsub = r.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"SSE stream opened for user {user_id}")

            try:
                while True:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        break

                    # Non-blocking read from Redis (100ms timeout)
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=1.0,
                    )

                    if message and message["type"] == "message":
                        data = message.get("data", "{}")
                        try:
                            parsed = json.loads(data)
                            event_type = parsed.get("type", "message")
                            yield f"event: {event_type}\ndata: {data}\n\n"
                        except Exception:
                            yield f"data: {data}\n\n"
                    else:
                        # Send periodic heartbeat to prevent proxy timeout
                        yield f"event: heartbeat\ndata: {{}}\n\n"
                        await asyncio.sleep(HEARTBEAT_INTERVAL)

            except asyncio.CancelledError:
                pass
            finally:
                await pubsub.unsubscribe(channel)
                logger.info(f"SSE stream closed for user {user_id}")

        else:
            # No Redis — just send heartbeats so the connection stays open
            logger.warning("SSE: Redis not available, heartbeat-only mode")
            while True:
                if await request.is_disconnected():
                    break
                yield f"event: heartbeat\ndata: {{}}\n\n"
                await asyncio.sleep(HEARTBEAT_INTERVAL)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        },
    )


async def publish_event(user_id: str, event_data: dict):
    """
    Publish a real-time event to a specific user's SSE channel via Redis.
    """
    try:
        r = await get_redis()
        if r:
            channel = f"user:{user_id}:events"
            await r.publish(channel, json.dumps(event_data))
    except Exception as e:
        logger.error(f"Failed to publish SSE event to {user_id}: {e}")
