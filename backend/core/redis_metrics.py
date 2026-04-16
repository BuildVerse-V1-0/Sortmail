"""
In-process Redis Metrics
------------------------
Tracks Redis command activity for quick observability.
"""

from __future__ import annotations

from collections import Counter, deque
from datetime import datetime, timezone
from threading import Lock
from time import monotonic
from typing import Any

_WINDOW_SECONDS = 60.0
_timestamps: deque[tuple[float, str]] = deque()
_totals: Counter[str] = Counter()
_lock = Lock()


def record_redis_call(command: str) -> None:
    """Record a Redis command execution for rolling per-minute metrics."""
    cmd = (command or "UNKNOWN").upper()
    now = monotonic()

    with _lock:
        _timestamps.append((now, cmd))
        _totals[cmd] += 1
        _trim_locked(now)


def get_redis_metrics_snapshot() -> dict[str, Any]:
    """Return rolling 60-second and lifetime Redis usage stats."""
    now = monotonic()
    with _lock:
        _trim_locked(now)
        recent_commands = [cmd for _, cmd in _timestamps]
        calls_last_minute = len(recent_commands)
        command_breakdown_last_minute = Counter(recent_commands)
        lifetime_breakdown = dict(_totals)

    return {
        "window_seconds": int(_WINDOW_SECONDS),
        "calls_last_minute": calls_last_minute,
        "commands_last_minute": dict(command_breakdown_last_minute),
        "total_calls_lifetime": sum(lifetime_breakdown.values()),
        "commands_lifetime": lifetime_breakdown,
        "sampled_at": datetime.now(timezone.utc).isoformat(),
    }


def get_redis_metrics_detail() -> dict[str, Any]:
    """Return detailed, copy-paste-friendly Redis command diagnostics."""
    now = monotonic()
    sampled_at = datetime.now(timezone.utc).isoformat()

    with _lock:
        _trim_locked(now)

        entries = list(_timestamps)
        totals = dict(_totals)

    def _count_within(seconds: float) -> int:
        cutoff = now - seconds
        return sum(1 for ts, _ in entries if ts >= cutoff)

    calls_last_10s = _count_within(10.0)
    calls_last_30s = _count_within(30.0)
    calls_last_60s = _count_within(60.0)
    calls_last_300s = _count_within(300.0)

    command_breakdown_300s: Counter[str] = Counter()
    cutoff_300 = now - 300.0
    for ts, cmd in entries:
        if ts >= cutoff_300:
            command_breakdown_300s[cmd] += 1

    # 5-second buckets over the last 60 seconds.
    timeline_window = 60
    bucket_seconds = 5
    bucket_count = timeline_window // bucket_seconds
    bucket_start = now - timeline_window
    buckets = [0 for _ in range(bucket_count)]
    for ts, _ in entries:
        if ts < bucket_start:
            continue
        idx = int((ts - bucket_start) // bucket_seconds)
        if 0 <= idx < bucket_count:
            buckets[idx] += 1

    timeline = [
        {
            "bucket_index": i,
            "seconds_ago_start": timeline_window - (i + 1) * bucket_seconds,
            "seconds_ago_end": timeline_window - i * bucket_seconds,
            "calls": buckets[i],
        }
        for i in range(bucket_count)
    ]

    recent = entries[-50:]
    recent_commands = [
        {
            "command": cmd,
            "age_seconds": round(max(0.0, now - ts), 3),
        }
        for ts, cmd in reversed(recent)
    ]

    top_300 = sorted(command_breakdown_300s.items(), key=lambda x: x[1], reverse=True)[:20]

    return {
        "sampled_at": sampled_at,
        "window_summary": {
            "calls_last_10s": calls_last_10s,
            "calls_last_30s": calls_last_30s,
            "calls_last_60s": calls_last_60s,
            "calls_last_300s": calls_last_300s,
        },
        "command_breakdown_last_300s": dict(command_breakdown_300s),
        "top_commands_last_300s": [{"command": cmd, "calls": calls} for cmd, calls in top_300],
        "timeline_last_60s_5s_buckets": timeline,
        "recent_calls": recent_commands,
        "lifetime": {
            "total_calls": sum(totals.values()),
            "commands": totals,
        },
    }


def _trim_locked(now: float) -> None:
    cutoff = now - _WINDOW_SECONDS
    while _timestamps and _timestamps[0][0] < cutoff:
        _timestamps.popleft()
