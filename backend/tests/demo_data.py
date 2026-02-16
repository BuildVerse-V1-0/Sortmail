"""
Demo Data — Realistic Test Cases
================================
This file contains realistic email scenarios for testing all modules.
Each team can use this data to verify their implementation works correctly.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

# ============================================================================
# SCENARIO 1: High Priority - Contract Review with Deadline
# ============================================================================

SCENARIO_1_RAW_EMAIL = {
    "thread_id": "thread_contract_001",
    "subject": "RE: Contract Review - Final Terms for Q1 Partnership",
    "participants": [
        "sarah.chen@bigclient.com",
        "you@company.com",
        "legal@company.com"
    ],
    "messages": [
        {
            "message_id": "msg_001_1",
            "from_address": "sarah.chen@bigclient.com",
            "to_addresses": ["you@company.com", "legal@company.com"],
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "body_text": """
Hi Team,

Please find attached the final contract with updated terms. Key changes from our last discussion:

1. Payment terms moved to NET 30 (from NET 45)
2. Liability cap increased to $500,000
3. Added Section 8.3 regarding data protection

I need your approval by Friday EOD (Jan 24) so we can proceed with signing next week.

Let me know if you have any questions!

Best regards,
Sarah Chen
VP of Partnerships
BigClient Inc.
            """,
            "has_attachments": True
        },
        {
            "message_id": "msg_001_2", 
            "from_address": "you@company.com",
            "to_addresses": ["sarah.chen@bigclient.com"],
            "timestamp": (datetime.now() - timedelta(hours=26)).isoformat(),
            "body_text": """
Hi Sarah,

Thanks for sending this over. I'll review with our legal team and get back to you by the end of the week.

Best,
You
            """
        }
    ],
    "attachments": [
        {
            "attachment_id": "att_001",
            "filename": "Contract_BigClient_Q1_2026_Final.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 245000
        }
    ]
}

# Expected output from Intelligence module
SCENARIO_1_EXPECTED_INTEL = {
    "thread_id": "thread_contract_001",
    "summary": "Sarah from BigClient sent the final contract with updated payment terms (NET 30), increased liability cap ($500K), and new data protection clause. She needs approval by Friday EOD (Jan 24) to proceed with signing.",
    "intent": "ACTION_REQUIRED",
    "urgency_score": 85,
    "main_ask": "Approve or request changes to the contract by Friday EOD",
    "extracted_deadlines": [
        {
            "deadline": "2026-01-24T17:00:00",
            "confidence": 0.95,
            "source_text": "by Friday EOD (Jan 24)"
        }
    ],
    "extracted_entities": [
        {"type": "person", "value": "Sarah Chen", "role": "VP of Partnerships"},
        {"type": "company", "value": "BigClient Inc."},
        {"type": "money", "value": "$500,000", "context": "liability cap"}
    ],
    "attachment_summaries": [
        {
            "filename": "Contract_BigClient_Q1_2026_Final.pdf",
            "summary": "Partnership contract with updated terms: NET 30 payment, $500K liability cap, GDPR-compliant data protection clause.",
            "key_points": [
                "Payment terms: NET 30",
                "Liability cap: $500,000",
                "New Section 8.3: Data Protection"
            ],
            "importance": "high"
        }
    ]
}

# Expected output from Workflow module
SCENARIO_1_EXPECTED_TASK = {
    "task_id": "task_001",
    "thread_id": "thread_contract_001",
    "title": "Reply to Sarah - Contract Review Approval",
    "task_type": "reply",
    "priority": "DO_NOW",
    "priority_score": 85,
    "priority_explanation": "Urgent deadline (Friday EOD) + Action required + VIP sender (VP level)",
    "effort": "deep_work",
    "deadline": "2026-01-24T17:00:00",
    "suggested_action": "Review contract terms and reply with approval or change requests"
}

# Expected draft from Workflow module
SCENARIO_1_EXPECTED_DRAFT = {
    "draft_id": "draft_001",
    "thread_id": "thread_contract_001",
    "tone": "formal",
    "content": """Hi Sarah,

Thank you for sending over the final contract with the updated terms.

I've reviewed the changes and [approve the terms / have the following concerns: SPECIFIC_CONCERN].

Regarding the key updates:
- NET 30 payment terms: Acknowledged
- $500,000 liability cap: Acknowledged  
- Section 8.3 Data Protection: [Reviewed and approved / Need clarification on SPECIFIC_POINT]

I'll have this finalized by Friday EOD as requested.

Best regards,
[Your name]""",
    "placeholders": [
        {"text": "[approve the terms / have the following concerns: SPECIFIC_CONCERN]", "type": "decision"},
        {"text": "[Reviewed and approved / Need clarification on SPECIFIC_POINT]", "type": "decision"},
        {"text": "[Your name]", "type": "auto_fill"}
    ],
    "references_attachments": True,
    "references_deadlines": True
}


# ============================================================================
# SCENARIO 2: Medium Priority - FYI with No Action Required
# ============================================================================

SCENARIO_2_RAW_EMAIL = {
    "thread_id": "thread_fyi_002",
    "subject": "Team Standup Notes - January 17",
    "participants": [
        "engineering-team@company.com",
        "pm@company.com"
    ],
    "messages": [
        {
            "message_id": "msg_002_1",
            "from_address": "pm@company.com",
            "to_addresses": ["engineering-team@company.com"],
            "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
            "body_text": """
Hi Team,

Here are the notes from today's standup:

**Completed:**
- API authentication module - DONE
- Database migration scripts - DONE

**In Progress:**
- Frontend dashboard (70% complete)
- Email sync integration (50% complete)

**Blockers:**
- Waiting on Gemini API approval from Google

**Next Steps:**
- Continue dashboard work
- Follow up on API approval

Let me know if I missed anything!

Cheers,
PM
            """,
            "has_attachments": False
        }
    ],
    "attachments": []
}

SCENARIO_2_EXPECTED_INTEL = {
    "thread_id": "thread_fyi_002",
    "summary": "Weekly standup notes: Auth and DB migrations completed. Dashboard at 70%, email sync at 50%. Blocked on Gemini API approval.",
    "intent": "FYI",
    "urgency_score": 20,
    "main_ask": None,
    "extracted_deadlines": [],
    "extracted_entities": []
}

SCENARIO_2_EXPECTED_TASK = {
    "task_id": "task_002",
    "thread_id": "thread_fyi_002",
    "title": "Review standup notes",
    "task_type": "other",
    "priority": "CAN_WAIT",
    "priority_score": 20,
    "priority_explanation": "FYI only - no action required",
    "effort": "quick",
    "deadline": None,
    "suggested_action": "Read and archive"
}


# ============================================================================
# SCENARIO 3: Scheduling Request - Meeting Needed
# ============================================================================

SCENARIO_3_RAW_EMAIL = {
    "thread_id": "thread_meeting_003",
    "subject": "Sync call to discuss Q2 roadmap?",
    "participants": [
        "marketing-lead@company.com",
        "you@company.com"
    ],
    "messages": [
        {
            "message_id": "msg_003_1",
            "from_address": "marketing-lead@company.com",
            "to_addresses": ["you@company.com"],
            "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
            "body_text": """
Hey!

Would love to sync on the Q2 roadmap - specifically around the new features we discussed last week.

Does Tuesday at 2pm work for you? Should only need 30 minutes.

Let me know!
- Marketing Lead
            """,
            "has_attachments": False
        }
    ],
    "attachments": []
}

SCENARIO_3_EXPECTED_INTEL = {
    "thread_id": "thread_meeting_003",
    "summary": "Marketing lead wants to schedule a 30-minute sync about Q2 roadmap and new features. Proposed time: Tuesday at 2pm.",
    "intent": "SCHEDULING",
    "urgency_score": 50,
    "main_ask": "Confirm or propose alternative time for sync call",
    "extracted_deadlines": [
        {
            "deadline": "2026-01-21T14:00:00",  # Next Tuesday
            "confidence": 0.8,
            "source_text": "Tuesday at 2pm"
        }
    ],
    "extracted_entities": []
}

SCENARIO_3_EXPECTED_CALENDAR = {
    "suggestion_id": "cal_001",
    "thread_id": "thread_meeting_003",
    "title": "Sync: Q2 Roadmap Discussion",
    "suggested_time": "2026-01-21T14:00:00",
    "duration_minutes": 30,
    "extracted_from": "Tuesday at 2pm... Should only need 30 minutes"
}


# ============================================================================
# SCENARIO 4: Waiting For Reply - Follow-up Needed
# ============================================================================

SCENARIO_4_RAW_EMAIL = {
    "thread_id": "thread_waiting_004",
    "subject": "RE: Proposal for new partnership",
    "participants": [
        "potential-client@external.com",
        "you@company.com"
    ],
    "messages": [
        {
            "message_id": "msg_004_1",
            "from_address": "you@company.com",
            "to_addresses": ["potential-client@external.com"],
            "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
            "body_text": """
Hi John,

Following up on our call last week. I've attached the proposal we discussed.

Key highlights:
- 20% volume discount for annual commitment
- Dedicated support channel
- Custom integration options

Would love to schedule a follow-up call to discuss next steps.

Looking forward to hearing from you!

Best,
You
            """,
            "has_attachments": True
        }
    ],
    "attachments": [
        {
            "attachment_id": "att_004",
            "filename": "Partnership_Proposal_2026.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 156000
        }
    ]
}

SCENARIO_4_EXPECTED_WAITING_FOR = {
    "waiting_id": "waiting_001",
    "thread_id": "thread_waiting_004",
    "last_sent_at": (datetime.now() - timedelta(days=5)).isoformat(),
    "days_waiting": 5,
    "recipient": "potential-client@external.com",
    "subject": "RE: Proposal for new partnership",
    "suggested_followup": "Check in on proposal review status"
}


# ============================================================================
# ALL SCENARIOS COMBINED
# ============================================================================

ALL_TEST_SCENARIOS = {
    "scenario_1_contract": {
        "name": "High Priority Contract Review",
        "raw_email": SCENARIO_1_RAW_EMAIL,
        "expected_intel": SCENARIO_1_EXPECTED_INTEL,
        "expected_task": SCENARIO_1_EXPECTED_TASK,
        "expected_draft": SCENARIO_1_EXPECTED_DRAFT
    },
    "scenario_2_fyi": {
        "name": "FYI Standup Notes",
        "raw_email": SCENARIO_2_RAW_EMAIL,
        "expected_intel": SCENARIO_2_EXPECTED_INTEL,
        "expected_task": SCENARIO_2_EXPECTED_TASK
    },
    "scenario_3_scheduling": {
        "name": "Meeting Request",
        "raw_email": SCENARIO_3_RAW_EMAIL,
        "expected_intel": SCENARIO_3_EXPECTED_INTEL,
        "expected_calendar": SCENARIO_3_EXPECTED_CALENDAR
    },
    "scenario_4_waiting": {
        "name": "Waiting for Reply",
        "raw_email": SCENARIO_4_RAW_EMAIL,
        "expected_waiting_for": SCENARIO_4_EXPECTED_WAITING_FOR
    }
}


def print_scenario(scenario_name: str):
    """Pretty print a scenario for debugging."""
    import json
    scenario = ALL_TEST_SCENARIOS.get(scenario_name)
    if scenario:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']}")
        print('='*60)
        print(json.dumps(scenario, indent=2, default=str))
    else:
        print(f"Unknown scenario: {scenario_name}")


if __name__ == "__main__":
    # Print all scenarios
    for key in ALL_TEST_SCENARIOS:
        print_scenario(key)
