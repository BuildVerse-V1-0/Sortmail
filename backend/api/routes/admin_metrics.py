"""
Admin Metrics Routes
--------------------
Admin-only observability endpoints.
"""

from time import monotonic
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import String, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.ai import AIUsageLog
from models.thread import Thread
from models.email import Email
from models.draft import Draft
from models.credits import UserCredits, PlanType, CreditTransaction, TransactionType
from models.billing import Invoice, InvoiceStatus, Subscription, SubscriptionStatus
from core.credits.token_pricing import milli_to_credits

from api.dependencies import get_current_user
from core.app_metrics import get_metrics_snapshot
from core.redis_metrics import get_redis_metrics_snapshot, get_redis_metrics_detail
from core.redis import get_redis, get_redis_pubsub
from app.config import settings
from core.intelligence.processing_queue import get_queue
from core.storage.database import get_db

router = APIRouter()

_QUEUE_SIZE_CACHE_TTL_SECONDS = 20.0
_queue_size_cache_value: int | None = None
_queue_size_cache_ts: float = 0.0


async def _get_queue_size_cached() -> tuple[bool, int | None]:
    global _queue_size_cache_value, _queue_size_cache_ts

    queue_enabled = bool(getattr(settings, "REDIS_URL", None))
    if not queue_enabled:
        return False, None

    now = monotonic()
    if (now - _queue_size_cache_ts) < _QUEUE_SIZE_CACHE_TTL_SECONDS:
        return True, _queue_size_cache_value

    queue_size: int | None = None
    try:
        queue = get_queue(settings.REDIS_URL)
        queue_size = await queue.size()
    except Exception:
        queue_size = None

    _queue_size_cache_value = queue_size
    _queue_size_cache_ts = now
    return True, queue_size


async def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/overview")
async def metrics_overview(admin: User = Depends(require_superuser)):
    _ = admin

    queue_enabled, queue_size = await _get_queue_size_cached()

    return {
        "app": get_metrics_snapshot(),
        "redis": get_redis_metrics_snapshot(),
        "queue": {
            "enabled": queue_enabled,
            "pending_items": queue_size,
        },
    }


@router.get("/app")
async def app_metrics(admin: User = Depends(require_superuser)):
    _ = admin
    return get_metrics_snapshot()


@router.get("/redis")
async def redis_metrics(admin: User = Depends(require_superuser)):
    _ = admin
    return get_redis_metrics_snapshot()


def _serialize_pool(pool) -> dict:
    max_connections = getattr(pool, "max_connections", None)

    in_use = getattr(pool, "_in_use_connections", None)
    available = getattr(pool, "_available_connections", None)

    try:
        in_use_count = len(in_use) if in_use is not None else None
    except Exception:
        in_use_count = None

    try:
        available_count = len(available) if available is not None else None
    except Exception:
        available_count = None

    utilization_pct = None
    if isinstance(max_connections, int) and max_connections > 0 and isinstance(in_use_count, int):
        utilization_pct = round((in_use_count / max_connections) * 100, 2)

    return {
        "max_connections": max_connections,
        "in_use_connections": in_use_count,
        "available_connections": available_count,
        "utilization_pct": utilization_pct,
    }


async def _safe_redis_info(client, section: str) -> dict | None:
    try:
        return await client.info(section)
    except Exception:
        return None


@router.get("/redis/detail")
async def redis_metrics_detail(admin: User = Depends(require_superuser)):
    _ = admin

    in_process = get_redis_metrics_detail()

    diagnostics = {
        "in_process": in_process,
        "clients": None,
        "stats": None,
        "memory": None,
        "command_pool": None,
        "pubsub_pool": None,
        "errors": [],
    }

    try:
        redis_cmd = await get_redis()
        diagnostics["command_pool"] = _serialize_pool(getattr(redis_cmd, "connection_pool", None))
        diagnostics["clients"] = await _safe_redis_info(redis_cmd, "clients")
        diagnostics["stats"] = await _safe_redis_info(redis_cmd, "stats")
        diagnostics["memory"] = await _safe_redis_info(redis_cmd, "memory")
    except Exception as exc:
        diagnostics["errors"].append(f"command_client_error: {str(exc)}")

    try:
        redis_pubsub = await get_redis_pubsub()
        diagnostics["pubsub_pool"] = _serialize_pool(getattr(redis_pubsub, "connection_pool", None))
    except Exception as exc:
        diagnostics["errors"].append(f"pubsub_client_error: {str(exc)}")

    return diagnostics


@router.get("/queue")
async def queue_metrics(admin: User = Depends(require_superuser)):
    _ = admin

    queue_enabled, pending_items = await _get_queue_size_cached()
    if not queue_enabled:
        return {
            "enabled": False,
            "pending_items": None,
        }

    return {
        "enabled": True,
        "pending_items": pending_items,
    }


@router.get("/ai-usage")
async def ai_usage_metrics(
    hours: int = 24,
    limit: int = 200,
    user_id: str | None = None,
    related_entity_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_superuser),
):
    _ = admin

    safe_hours = min(max(int(hours or 24), 1), 24 * 30)
    safe_limit = min(max(int(limit or 200), 1), 1000)
    since_ts = datetime.now(timezone.utc) - timedelta(hours=safe_hours)

    filters = [AIUsageLog.created_at >= since_ts]
    if user_id:
        filters.append(AIUsageLog.user_id == user_id)
    if related_entity_id:
        filters.append(AIUsageLog.related_entity_id == related_entity_id)

    totals_stmt = select(
        func.count(AIUsageLog.id),
        func.coalesce(func.sum(AIUsageLog.tokens_input), 0),
        func.coalesce(func.sum(AIUsageLog.tokens_output), 0),
        func.coalesce(func.sum(AIUsageLog.tokens_total), 0),
        func.coalesce(func.sum(AIUsageLog.cost_cents), 0),
        func.coalesce(func.sum(case((AIUsageLog.error_occurred.is_(True), 1), else_=0)), 0),
    ).where(*filters)
    totals_row = (await db.execute(totals_stmt)).one()

    lower_model = func.lower(AIUsageLog.model_name)
    bedrock_model_expr = (
        lower_model.like("%amazon%")
        | lower_model.like("%nova%")
        | lower_model.like("%bedrock%")
    )

    bedrock_totals_stmt = select(
        func.count(AIUsageLog.id),
        func.coalesce(func.sum(AIUsageLog.tokens_input), 0),
        func.coalesce(func.sum(AIUsageLog.tokens_output), 0),
        func.coalesce(func.sum(AIUsageLog.tokens_total), 0),
        func.coalesce(func.sum(AIUsageLog.cost_cents), 0),
        func.coalesce(func.sum(case((AIUsageLog.error_occurred.is_(True), 1), else_=0)), 0),
    ).where(*filters, bedrock_model_expr)
    bedrock_totals_row = (await db.execute(bedrock_totals_stmt)).one()

    by_user_stmt = (
        select(
            AIUsageLog.user_id,
            func.count(AIUsageLog.id).label("calls"),
            func.coalesce(func.sum(AIUsageLog.tokens_total), 0).label("tokens_total"),
        )
        .where(*filters)
        .group_by(AIUsageLog.user_id)
        .order_by(func.coalesce(func.sum(AIUsageLog.tokens_total), 0).desc())
        .limit(50)
    )
    by_user_rows = (await db.execute(by_user_stmt)).all()

    by_model_stmt = (
        select(
            AIUsageLog.model_name,
            func.count(AIUsageLog.id).label("calls"),
            func.coalesce(func.sum(AIUsageLog.tokens_input), 0).label("tokens_input"),
            func.coalesce(func.sum(AIUsageLog.tokens_output), 0).label("tokens_output"),
            func.coalesce(func.sum(AIUsageLog.tokens_total), 0).label("tokens_total"),
            func.coalesce(func.avg(AIUsageLog.latency_ms), 0).label("avg_latency_ms"),
            func.coalesce(func.sum(case((AIUsageLog.error_occurred.is_(True), 1), else_=0)), 0).label("errors"),
        )
        .where(*filters)
        .group_by(AIUsageLog.model_name)
        .order_by(func.coalesce(func.sum(AIUsageLog.tokens_total), 0).desc())
        .limit(20)
    )
    by_model_rows = (await db.execute(by_model_stmt)).all()

    by_operation_stmt = (
        select(
            AIUsageLog.operation_type,
            func.count(AIUsageLog.id).label("calls"),
            func.coalesce(func.sum(AIUsageLog.tokens_total), 0).label("tokens_total"),
            func.coalesce(func.sum(AIUsageLog.cost_cents), 0).label("cost_cents"),
        )
        .where(*filters)
        .group_by(AIUsageLog.operation_type)
        .order_by(func.coalesce(func.sum(AIUsageLog.tokens_total), 0).desc())
        .limit(20)
    )
    by_operation_rows = (await db.execute(by_operation_stmt)).all()

    operation_totals: dict[str, int] = {
        str(row[0] or "").upper(): int(row[1] or 0)
        for row in by_operation_rows
    }
    pass1_calls = int(operation_totals.get("THREAD_INTEL_PASS1", 0))
    pass2_calls = int(operation_totals.get("THREAD_INTEL_PASS2", 0))
    pass1_only_estimated = max(pass1_calls - pass2_calls, 0)
    pass2_execution_rate_pct = round((pass2_calls / pass1_calls) * 100, 3) if pass1_calls else 0.0

    rows_stmt = (
        select(AIUsageLog)
        .where(*filters)
        .order_by(AIUsageLog.created_at.desc())
        .limit(safe_limit)
    )
    rows = (await db.execute(rows_stmt)).scalars().all()

    row_user_ids = {str(row.user_id) for row in rows if row.user_id}
    user_identity_map: dict[str, dict[str, str | None]] = {}
    user_plan_map: dict[str, str] = {}
    if row_user_ids:
        user_rows = (
            await db.execute(
                select(User.id, User.email, User.name).where(User.id.in_(row_user_ids))
            )
        ).all()
        user_identity_map = {
            str(uid): {
                "email": email,
                "name": name,
            }
            for uid, email, name in user_rows
        }

        plan_rows = (
            await db.execute(
                select(UserCredits.user_id, UserCredits.plan).where(UserCredits.user_id.in_(row_user_ids))
            )
        ).all()
        user_plan_map = {
            str(uid): (plan.value if plan else PlanType.FREE.value)
            for uid, plan in plan_rows
        }

    thread_ids = {
        str(row.related_entity_id)
        for row in rows
        if row.related_entity_id and (row.related_entity_type or "").lower() == "thread"
    }
    email_ids = {
        str(row.related_entity_id)
        for row in rows
        if row.related_entity_id and (row.related_entity_type or "").lower() == "email"
    }
    draft_ids = {
        str(row.related_entity_id)
        for row in rows
        if row.related_entity_id and (row.related_entity_type or "").lower() == "draft"
    }

    thread_preview_map: dict[str, dict[str, str | None]] = {}
    email_preview_map: dict[str, dict[str, str | None]] = {}
    draft_preview_map: dict[str, dict[str, str | None]] = {}

    if thread_ids:
        thread_rows = (
            await db.execute(
                select(Thread.id, Thread.subject, Thread.external_id).where(Thread.id.in_(thread_ids))
            )
        ).all()
        thread_preview_map = {
            str(thread_id): {
                "subject": subject,
                "external_id": external_id,
            }
            for thread_id, subject, external_id in thread_rows
        }

    if email_ids:
        email_rows = (
            await db.execute(
                select(Email.id, Email.subject, Email.sender, Email.snippet).where(Email.id.in_(email_ids))
            )
        ).all()
        email_preview_map = {
            str(email_id): {
                "subject": subject,
                "sender": sender,
                "snippet": snippet,
            }
            for email_id, subject, sender, snippet in email_rows
        }

    if draft_ids:
        draft_rows = (
            await db.execute(
                select(Draft.id, Draft.subject, Draft.thread_id).where(Draft.id.in_(draft_ids))
            )
        ).all()
        draft_preview_map = {
            str(draft_id): {
                "subject": subject,
                "thread_id": thread_id,
            }
            for draft_id, subject, thread_id in draft_rows
        }

    records = [
        {
            "id": row.id,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "user_id": row.user_id,
            "user_email": user_identity_map.get(str(row.user_id), {}).get("email"),
            "user_name": user_identity_map.get(str(row.user_id), {}).get("name"),
            "user_plan": user_plan_map.get(str(row.user_id), PlanType.FREE.value),
            "operation_type": row.operation_type,
            "model_name": row.model_name,
            "provider": row.provider.value if row.provider else None,
            "tokens_input": row.tokens_input,
            "tokens_output": row.tokens_output,
            "tokens_total": row.tokens_total,
            "cost_cents": row.cost_cents,
            "credits_charged": round(milli_to_credits(int(row.credits_charged or 0)), 3),
            "latency_ms": row.latency_ms,
            "related_entity_type": row.related_entity_type,
            "related_entity_id": row.related_entity_id,
            "related_entity_preview": (
                thread_preview_map.get(str(row.related_entity_id))
                if (row.related_entity_type or "").lower() == "thread"
                else email_preview_map.get(str(row.related_entity_id))
                if (row.related_entity_type or "").lower() == "email"
                else draft_preview_map.get(str(row.related_entity_id))
                if (row.related_entity_type or "").lower() == "draft"
                else None
            ),
            "request_id": row.request_id,
            "error_occurred": row.error_occurred,
            "error_type": row.error_type,
            "cache_hit": row.cache_hit,
            "token_source": (row.metadata_json or {}).get("token_source"),
            "provider_cost_usd": round(_as_float(((row.metadata_json or {}).get("pricing") or {}).get("provider_cost_usd"), float((row.cost_cents or 0) / 100.0)), 8),
            "user_billable_usd": round(_as_float(((row.metadata_json or {}).get("pricing") or {}).get("user_billable_usd"), 0.0), 8),
            "implied_margin_usd": round(
                _as_float(((row.metadata_json or {}).get("pricing") or {}).get("user_billable_usd"), 0.0)
                - _as_float(((row.metadata_json or {}).get("pricing") or {}).get("provider_cost_usd"), float((row.cost_cents or 0) / 100.0)),
                8,
            ),
            "charged_milli_credits": int(((row.metadata_json or {}).get("pricing") or {}).get("charged_milli_credits") or 0),
            "balance_after": (row.metadata_json or {}).get("balance_after"),
            "charge_error": (row.metadata_json or {}).get("charge_error"),
            "metadata": row.metadata_json or {},
        }
        for row in rows
    ]

    total_calls = int(totals_row[0] or 0)
    total_tokens = int(totals_row[3] or 0)
    total_errors = int(totals_row[5] or 0)

    bedrock_calls = int(bedrock_totals_row[0] or 0)
    bedrock_tokens = int(bedrock_totals_row[3] or 0)
    bedrock_errors = int(bedrock_totals_row[5] or 0)

    return {
        "window": {
            "hours": safe_hours,
            "since": since_ts.isoformat(),
        },
        "filters": {
            "user_id": user_id,
            "related_entity_id": related_entity_id,
            "limit": safe_limit,
        },
        "totals": {
            "calls": total_calls,
            "tokens_input": int(totals_row[1] or 0),
            "tokens_output": int(totals_row[2] or 0),
            "tokens_total": total_tokens,
            "cost_cents": int(totals_row[4] or 0),
            "errors": total_errors,
            "avg_tokens_per_call": round((total_tokens / total_calls), 2) if total_calls else 0,
            "error_rate_pct": round((total_errors / total_calls) * 100, 3) if total_calls else 0,
        },
        "bedrock": {
            "calls": bedrock_calls,
            "tokens_input": int(bedrock_totals_row[1] or 0),
            "tokens_output": int(bedrock_totals_row[2] or 0),
            "tokens_total": bedrock_tokens,
            "cost_cents": int(bedrock_totals_row[4] or 0),
            "errors": bedrock_errors,
            "avg_tokens_per_call": round((bedrock_tokens / bedrock_calls), 2) if bedrock_calls else 0,
            "error_rate_pct": round((bedrock_errors / bedrock_calls) * 100, 3) if bedrock_calls else 0,
        },
        "by_user": [
            {
                "user_id": row[0],
                "calls": int(row[1] or 0),
                "tokens_total": int(row[2] or 0),
            }
            for row in by_user_rows
        ],
        "by_model": [
            {
                "model_name": row[0],
                "calls": int(row[1] or 0),
                "tokens_input": int(row[2] or 0),
                "tokens_output": int(row[3] or 0),
                "tokens_total": int(row[4] or 0),
                "avg_latency_ms": round(float(row[5] or 0), 2),
                "errors": int(row[6] or 0),
            }
            for row in by_model_rows
        ],
        "by_operation": [
            {
                "operation_type": row[0],
                "calls": int(row[1] or 0),
                "tokens_total": int(row[2] or 0),
                "cost_cents": int(row[3] or 0),
            }
            for row in by_operation_rows
        ],
        "two_pass": {
            "pass1_calls": pass1_calls,
            "pass2_calls": pass2_calls,
            "pass1_only_estimated": pass1_only_estimated,
            "pass2_execution_rate_pct": pass2_execution_rate_pct,
        },
        "records": records,
    }


def _as_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


@router.get("/economics")
async def economics_metrics(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_superuser),
):
    """Detailed burn/earn economics for AI usage and paid subscriptions."""
    _ = admin
    safe_days = min(max(int(days or 30), 1), 365)
    since_ts = datetime.now(timezone.utc) - timedelta(days=safe_days)

    # Build user->plan map for usage attribution.
    credits_rows = (await db.execute(select(UserCredits.user_id, UserCredits.plan))).all()
    user_plan_map = {
        str(user_id): (plan.value if plan else PlanType.FREE.value)
        for user_id, plan in credits_rows
    }

    usage_rows = (
        await db.execute(
            select(AIUsageLog).where(AIUsageLog.created_at >= since_ts).order_by(AIUsageLog.created_at.asc())
        )
    ).scalars().all()

    totals = {
        "calls": 0,
        "tokens_input": 0,
        "tokens_output": 0,
        "tokens_total": 0,
        "provider_cost_usd": 0.0,
        "user_billable_usd": 0.0,
        "implied_margin_usd": 0.0,
        "credits_charged": 0,
        "charge_failures": 0,
    }

    by_plan: dict[str, dict[str, float | int]] = {}
    by_model: dict[str, dict[str, float | int]] = {}
    by_operation: dict[str, dict[str, float | int]] = {}

    for row in usage_rows:
        md = row.metadata_json or {}
        pricing = md.get("pricing") if isinstance(md.get("pricing"), dict) else {}

        provider_cost_usd = _as_float(pricing.get("provider_cost_usd"), default=float((row.cost_cents or 0) / 100.0))
        user_billable_usd = _as_float(pricing.get("user_billable_usd"), default=0.0)
        credits_charged = int(row.credits_charged or 0)

        plan = user_plan_map.get(str(row.user_id), PlanType.FREE.value)
        model = row.model_name or "unknown"
        operation = row.operation_type or "unknown"

        totals["calls"] += 1
        totals["tokens_input"] += int(row.tokens_input or 0)
        totals["tokens_output"] += int(row.tokens_output or 0)
        totals["tokens_total"] += int(row.tokens_total or 0)
        totals["provider_cost_usd"] += provider_cost_usd
        totals["user_billable_usd"] += user_billable_usd
        totals["implied_margin_usd"] += (user_billable_usd - provider_cost_usd)
        totals["credits_charged"] += credits_charged
        if md.get("charge_error"):
            totals["charge_failures"] += 1

        if plan not in by_plan:
            by_plan[plan] = {
                "calls": 0,
                "tokens_total": 0,
                "provider_cost_usd": 0.0,
                "user_billable_usd": 0.0,
                "implied_margin_usd": 0.0,
                "credits_charged": 0,
            }
        by_plan[plan]["calls"] += 1
        by_plan[plan]["tokens_total"] += int(row.tokens_total or 0)
        by_plan[plan]["provider_cost_usd"] += provider_cost_usd
        by_plan[plan]["user_billable_usd"] += user_billable_usd
        by_plan[plan]["implied_margin_usd"] += (user_billable_usd - provider_cost_usd)
        by_plan[plan]["credits_charged"] += credits_charged

        if model not in by_model:
            by_model[model] = {
                "calls": 0,
                "tokens_total": 0,
                "provider_cost_usd": 0.0,
                "user_billable_usd": 0.0,
                "implied_margin_usd": 0.0,
            }
        by_model[model]["calls"] += 1
        by_model[model]["tokens_total"] += int(row.tokens_total or 0)
        by_model[model]["provider_cost_usd"] += provider_cost_usd
        by_model[model]["user_billable_usd"] += user_billable_usd
        by_model[model]["implied_margin_usd"] += (user_billable_usd - provider_cost_usd)

        if operation not in by_operation:
            by_operation[operation] = {
                "calls": 0,
                "tokens_total": 0,
                "provider_cost_usd": 0.0,
                "user_billable_usd": 0.0,
                "implied_margin_usd": 0.0,
            }
        by_operation[operation]["calls"] += 1
        by_operation[operation]["tokens_total"] += int(row.tokens_total or 0)
        by_operation[operation]["provider_cost_usd"] += provider_cost_usd
        by_operation[operation]["user_billable_usd"] += user_billable_usd
        by_operation[operation]["implied_margin_usd"] += (user_billable_usd - provider_cost_usd)

    # Paid revenue signals: invoices and explicit purchase transactions.
    paid_invoice_stmt = select(func.coalesce(func.sum(Invoice.amount_cents), 0)).where(
        cast(Invoice.status, String) == InvoiceStatus.PAID.value,
        Invoice.created_at >= since_ts,
    )
    paid_invoice_cents = int((await db.execute(paid_invoice_stmt)).scalar() or 0)

    purchase_rows = (
        await db.execute(
            select(CreditTransaction).where(
                CreditTransaction.created_at >= since_ts,
                CreditTransaction.transaction_type == TransactionType.PURCHASE,
            )
        )
    ).scalars().all()
    purchase_revenue_usd = 0.0
    for tx in purchase_rows:
        md = tx.metadata_json or {}
        purchase_revenue_usd += _as_float(md.get("purchase_usd"), default=0.0)

    active_subscriptions_stmt = select(func.count(Subscription.id)).where(
        cast(Subscription.status, String).in_(
            [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value]
        ),
    )
    active_subscriptions = int((await db.execute(active_subscriptions_stmt)).scalar() or 0)

    free_provider_burn = _as_float(by_plan.get(PlanType.FREE.value, {}).get("provider_cost_usd"), 0.0)
    paid_provider_cost = 0.0
    paid_implied_margin = 0.0
    for plan_name, values in by_plan.items():
        if plan_name != PlanType.FREE.value:
            paid_provider_cost += _as_float(values.get("provider_cost_usd"), 0.0)
            paid_implied_margin += _as_float(values.get("implied_margin_usd"), 0.0)

    return {
        "window": {
            "days": safe_days,
            "since": since_ts.isoformat(),
        },
        "unit_economics": {
            "credit_unit_usd": 0.001,
            "token_pricing": {
                "provider_input_per_million_usd": 0.30,
                "provider_output_per_million_usd": 2.50,
                "user_input_per_million_usd": 1.20,
                "user_output_per_million_usd": 10.00,
                "nova_micro_provider_input_per_million_usd": 0.035,
                "nova_micro_provider_output_per_million_usd": 0.14,
                "nova_micro_user_input_per_million_usd": 0.14,
                "nova_micro_user_output_per_million_usd": 0.56,
            },
        },
        "totals": {
            **totals,
            "credits_charged": round(milli_to_credits(int(totals["credits_charged"])), 3),
            "provider_cost_usd": round(float(totals["provider_cost_usd"]), 6),
            "user_billable_usd": round(float(totals["user_billable_usd"]), 6),
            "implied_margin_usd": round(float(totals["implied_margin_usd"]), 6),
        },
        "financials": {
            "active_subscriptions": active_subscriptions,
            "subscription_revenue_usd": round(paid_invoice_cents / 100.0, 6),
            "credit_purchase_revenue_usd": round(purchase_revenue_usd, 6),
            "free_plan_burn_usd": round(free_provider_burn, 6),
            "paid_plan_provider_cost_usd": round(paid_provider_cost, 6),
            "paid_plan_implied_usage_margin_usd": round(paid_implied_margin, 6),
        },
        "by_plan": {
            plan: {
                "calls": int(values.get("calls", 0)),
                "tokens_total": int(values.get("tokens_total", 0)),
                "credits_charged": round(milli_to_credits(int(values.get("credits_charged", 0))), 3),
                "provider_cost_usd": round(_as_float(values.get("provider_cost_usd"), 0.0), 6),
                "user_billable_usd": round(_as_float(values.get("user_billable_usd"), 0.0), 6),
                "implied_margin_usd": round(_as_float(values.get("implied_margin_usd"), 0.0), 6),
            }
            for plan, values in by_plan.items()
        },
        "by_model": {
            model: {
                "calls": int(values.get("calls", 0)),
                "tokens_total": int(values.get("tokens_total", 0)),
                "provider_cost_usd": round(_as_float(values.get("provider_cost_usd"), 0.0), 6),
                "user_billable_usd": round(_as_float(values.get("user_billable_usd"), 0.0), 6),
                "implied_margin_usd": round(_as_float(values.get("implied_margin_usd"), 0.0), 6),
            }
            for model, values in by_model.items()
        },
        "by_operation": {
            op: {
                "calls": int(values.get("calls", 0)),
                "tokens_total": int(values.get("tokens_total", 0)),
                "provider_cost_usd": round(_as_float(values.get("provider_cost_usd"), 0.0), 6),
                "user_billable_usd": round(_as_float(values.get("user_billable_usd"), 0.0), 6),
                "implied_margin_usd": round(_as_float(values.get("implied_margin_usd"), 0.0), 6),
            }
            for op, values in by_operation.items()
        },
    }


@router.get("/economics/trends")
async def economics_trends(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_superuser),
):
    """Daily trend series grouped by day and plan for charting burn/earn dynamics."""
    _ = admin
    safe_days = min(max(int(days or 30), 1), 365)
    since_ts = datetime.now(timezone.utc) - timedelta(days=safe_days)

    credits_rows = (await db.execute(select(UserCredits.user_id, UserCredits.plan))).all()
    user_plan_map = {
        str(user_id): (plan.value if plan else PlanType.FREE.value)
        for user_id, plan in credits_rows
    }

    usage_rows = (
        await db.execute(
            select(AIUsageLog).where(AIUsageLog.created_at >= since_ts).order_by(AIUsageLog.created_at.asc())
        )
    ).scalars().all()

    trend: dict[tuple[str, str], dict[str, float | int]] = {}
    pass_trend: dict[str, dict[str, int]] = {}
    for row in usage_rows:
        md = row.metadata_json or {}
        pricing = md.get("pricing") if isinstance(md.get("pricing"), dict) else {}
        provider_cost_usd = _as_float(pricing.get("provider_cost_usd"), default=float((row.cost_cents or 0) / 100.0))
        user_billable_usd = _as_float(pricing.get("user_billable_usd"), default=0.0)
        plan = user_plan_map.get(str(row.user_id), PlanType.FREE.value)
        day = row.created_at.date().isoformat() if row.created_at else datetime.now(timezone.utc).date().isoformat()
        key = (day, plan)

        if key not in trend:
            trend[key] = {
                "calls": 0,
                "tokens_total": 0,
                "provider_cost_usd": 0.0,
                "user_billable_usd": 0.0,
                "implied_margin_usd": 0.0,
                "credits_charged_milli": 0,
            }

        trend[key]["calls"] += 1
        trend[key]["tokens_total"] += int(row.tokens_total or 0)
        trend[key]["provider_cost_usd"] += provider_cost_usd
        trend[key]["user_billable_usd"] += user_billable_usd
        trend[key]["implied_margin_usd"] += (user_billable_usd - provider_cost_usd)
        trend[key]["credits_charged_milli"] += int(row.credits_charged or 0)

        day_pass_key = day
        if day_pass_key not in pass_trend:
            pass_trend[day_pass_key] = {
                "pass1_calls": 0,
                "pass2_calls": 0,
            }
        op = str(row.operation_type or "").upper()
        if op == "THREAD_INTEL_PASS1":
            pass_trend[day_pass_key]["pass1_calls"] += 1
        elif op == "THREAD_INTEL_PASS2":
            pass_trend[day_pass_key]["pass2_calls"] += 1

    series = []
    for (day, plan), values in sorted(trend.items(), key=lambda item: (item[0][0], item[0][1])):
        milli = int(values.get("credits_charged_milli", 0))
        series.append(
            {
                "date": day,
                "plan": plan,
                "calls": int(values.get("calls", 0)),
                "tokens_total": int(values.get("tokens_total", 0)),
                "credits_charged": round(milli_to_credits(milli), 3),
                "provider_cost_usd": round(_as_float(values.get("provider_cost_usd"), 0.0), 6),
                "user_billable_usd": round(_as_float(values.get("user_billable_usd"), 0.0), 6),
                "implied_margin_usd": round(_as_float(values.get("implied_margin_usd"), 0.0), 6),
            }
        )

    return {
        "window": {
            "days": safe_days,
            "since": since_ts.isoformat(),
        },
        "series": series,
        "two_pass_series": [
            {
                "date": day,
                "pass1_calls": int(values.get("pass1_calls", 0)),
                "pass2_calls": int(values.get("pass2_calls", 0)),
                "pass1_only_estimated": max(
                    int(values.get("pass1_calls", 0)) - int(values.get("pass2_calls", 0)),
                    0,
                ),
                "pass2_execution_rate_pct": (
                    round((int(values.get("pass2_calls", 0)) / int(values.get("pass1_calls", 0))) * 100, 3)
                    if int(values.get("pass1_calls", 0))
                    else 0.0
                ),
            }
            for day, values in sorted(pass_trend.items(), key=lambda item: item[0])
        ],
    }
