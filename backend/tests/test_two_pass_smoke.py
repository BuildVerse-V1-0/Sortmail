import pytest

from core.credits.token_pricing import calculate_token_billing
from core.intelligence import pipeline
from models.thread import Thread


def _thread(subject: str = "Status Update") -> Thread:
    return Thread(
        id="thread-smoke",
        user_id="user-smoke",
        external_id="ext-smoke",
        provider="GMAIL",
        subject=subject,
        participants=["Sender <sender@example.com>"],
    )


def test_micro_model_pricing_is_lower_than_default():
    default_breakdown = calculate_token_billing(1000, 1000, model_name="us.amazon.nova-2-lite-v1:0")
    micro_breakdown = calculate_token_billing(1000, 1000, model_name="amazon.nova-micro-v1:0")

    # Nova Micro provider rates should be significantly cheaper than default Nova Lite config.
    assert micro_breakdown.provider_cost_usd < default_breakdown.provider_cost_usd
    assert micro_breakdown.user_billable_usd < default_breakdown.user_billable_usd


def test_should_run_second_pass_for_meeting_signal():
    thread = _thread()
    messages = [{"body": "Can we meet tomorrow at 3 PM?", "is_from_user": False}]
    micro_intel = {
        "intent": "FYI",
        "should_create_reply": False,
        "should_create_tasks": False,
        "meeting_detected": {"has_meeting": True},
        "action_items": [],
    }

    assert pipeline._should_run_second_pass(thread, messages, micro_intel) is True


@pytest.mark.asyncio
async def test_two_pass_smoke_executes_second_pass_only_when_needed(monkeypatch):
    thread = _thread(subject="Quarterly compliance event notification")
    messages = [{"body": "Important compliance event happens next week.", "is_from_user": False}]

    calls = []

    async def fake_run_intelligence_with_usage(**kwargs):
        operation = kwargs.get("operation")
        calls.append(operation)
        if operation == "thread_intel_pass1":
            return {
                "intel": {
                    "summary": "Compliance event alert",
                    "intent": "FYI",
                    "should_create_reply": False,
                    "should_create_tasks": False,
                    "meeting_detected": False,
                    "action_items": [],
                    "topics": ["compliance event"],
                },
                "input_tokens": 120,
                "output_tokens": 60,
                "latency_ms": 400,
                "token_source": "provider_reported",
            }
        return {
            "intel": {
                "summary": "Compliance event alert with owner actions",
                "intent": "ACTION_REQUIRED",
                "should_create_reply": True,
                "should_create_tasks": True,
                "action_items": [{"title": "Prepare compliance note"}],
            },
            "input_tokens": 240,
            "output_tokens": 120,
            "latency_ms": 900,
            "token_source": "provider_reported",
        }

    monkeypatch.setattr(pipeline, "run_intelligence_with_usage", fake_run_intelligence_with_usage)

    merged, meta = await pipeline._run_two_pass_intelligence(
        thread=thread,
        thread_id=str(thread.id),
        user_id=str(thread.user_id),
        subject=str(thread.subject),
        participants=list(thread.participants or []),
        messages=messages,
    )

    assert calls == ["thread_intel_pass1", "thread_intel_pass2"]
    assert meta["pass2_executed"] is True
    assert meta["pass1_input_tokens"] == 120
    assert meta["pass2_input_tokens"] == 240
    assert merged.get("intent") == "ACTION_REQUIRED"
    assert len(merged.get("action_items") or []) == 1


@pytest.mark.asyncio
async def test_two_pass_smoke_stops_at_pass1_for_low_value(monkeypatch):
    thread = _thread(subject="Weekly newsletter")
    messages = [{"body": "Unsubscribe and promo updates.", "is_from_user": False}]

    calls = []

    async def fake_run_intelligence_with_usage(**kwargs):
        operation = kwargs.get("operation")
        calls.append(operation)
        return {
            "intel": {
                "summary": "Promotional newsletter",
                "intent": "NEWSLETTER",
                "should_create_reply": False,
                "should_create_tasks": False,
                "meeting_detected": False,
                "action_items": [],
                "topics": ["promotion"],
            },
            "input_tokens": 80,
            "output_tokens": 40,
            "latency_ms": 200,
            "token_source": "provider_reported",
        }

    monkeypatch.setattr(pipeline, "run_intelligence_with_usage", fake_run_intelligence_with_usage)

    merged, meta = await pipeline._run_two_pass_intelligence(
        thread=thread,
        thread_id=str(thread.id),
        user_id=str(thread.user_id),
        subject=str(thread.subject),
        participants=list(thread.participants or []),
        messages=messages,
    )

    assert calls == ["thread_intel_pass1"]
    assert meta["pass2_executed"] is False
    assert merged.get("intent") == "NEWSLETTER"