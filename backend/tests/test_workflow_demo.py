"""
Test Runner for Workflow Module — Team C
=========================================
Run this to verify your workflow implementations work correctly.
"""

import sys
sys.path.insert(0, '..')

from datetime import datetime
from typing import Dict, Any
import json

# Import demo data
from demo_data import (
    SCENARIO_1_EXPECTED_INTEL,
    SCENARIO_1_EXPECTED_TASK,
    SCENARIO_1_EXPECTED_DRAFT,
    SCENARIO_2_EXPECTED_INTEL,
    SCENARIO_2_EXPECTED_TASK,
    SCENARIO_3_EXPECTED_INTEL,
    SCENARIO_3_EXPECTED_CALENDAR,
    SCENARIO_4_EXPECTED_WAITING_FOR
)

# Import your implementations (uncomment as you implement)
# from core.workflow.priority_engine import calculate_priority
# from core.workflow.task_generator import generate_tasks
# from core.workflow.draft_engine import generate_draft


def test_priority_engine():
    """Test the priority calculation module."""
    print("\n" + "="*60)
    print("TEST: Priority Engine")
    print("="*60)
    
    test_cases = [
        ("High Priority - Contract", SCENARIO_1_EXPECTED_INTEL, "DO_NOW", 85),
        ("Low Priority - FYI", SCENARIO_2_EXPECTED_INTEL, "CAN_WAIT", 20),
        ("Medium Priority - Meeting", SCENARIO_3_EXPECTED_INTEL, "DO_TODAY", 50),
    ]
    
    for name, intel, expected_level, expected_score in test_cases:
        print(f"\n📊 {name}:")
        print(f"  Intent: {intel['intent']}")
        print(f"  Urgency: {intel['urgency_score']}")
        print(f"  Has Deadline: {len(intel.get('extracted_deadlines', [])) > 0}")
        print(f"\n  ✅ Expected: {expected_level} (score: {expected_score})")
        # Uncomment when implemented:
        # result = calculate_priority(intel)
        # print(f"  🔧 Your Output: {result.priority} (score: {result.priority_score})")
        # print(f"     Explanation: {result.priority_explanation}")
        print(f"  🔧 Your Output: [NOT IMPLEMENTED]")


def test_task_generator():
    """Test the task generation module."""
    print("\n" + "="*60)
    print("TEST: Task Generator")
    print("="*60)
    
    print("\n📧 INPUT - ThreadIntelV1:")
    print(f"  Thread ID: {SCENARIO_1_EXPECTED_INTEL['thread_id']}")
    print(f"  Intent: {SCENARIO_1_EXPECTED_INTEL['intent']}")
    print(f"  Main Ask: {SCENARIO_1_EXPECTED_INTEL['main_ask']}")
    
    print("\n✅ EXPECTED TaskDTOv1:")
    print(json.dumps(SCENARIO_1_EXPECTED_TASK, indent=2, default=str))
    
    print("\n🔧 YOUR OUTPUT:")
    # Uncomment when implemented:
    # result = generate_tasks(SCENARIO_1_EXPECTED_INTEL)
    # print(json.dumps(result[0].dict(), indent=2, default=str))
    print("  [NOT IMPLEMENTED YET - Implement generate_tasks()]")
    
    print("\n📋 CHECKLIST:")
    print("  □ Task title is descriptive")
    print("  □ Priority matches urgency + intent")
    print("  □ Explanation is human-readable")
    print("  □ Deadline is extracted correctly")


def test_draft_generator():
    """Test the draft generation module."""
    print("\n" + "="*60)
    print("TEST: Draft Generator")
    print("="*60)
    
    print("\n📧 INPUT - Thread + Intel:")
    print(f"  Subject: Contract Review - Final Terms")
    print(f"  Intent: ACTION_REQUIRED")
    print(f"  Tone: formal")
    
    print("\n✅ EXPECTED DraftDTOv1:")
    print(f"  Content Preview: {SCENARIO_1_EXPECTED_DRAFT['content'][:100]}...")
    print(f"  Placeholders: {len(SCENARIO_1_EXPECTED_DRAFT['placeholders'])}")
    print(f"  References Attachments: {SCENARIO_1_EXPECTED_DRAFT['references_attachments']}")
    print(f"  References Deadlines: {SCENARIO_1_EXPECTED_DRAFT['references_deadlines']}")
    
    print("\n🔧 YOUR OUTPUT:")
    # Uncomment when implemented:
    # result = generate_draft(SCENARIO_1_EXPECTED_INTEL, tone="formal")
    # print(f"  Content: {result.content[:100]}...")
    print("  [NOT IMPLEMENTED YET - Implement generate_draft()]")
    
    print("\n📋 CHECKLIST:")
    print("  □ Draft addresses the sender by name")
    print("  □ Draft references the attachment")
    print("  □ Draft acknowledges the deadline")
    print("  □ Placeholders are marked with [brackets]")


def test_calendar_suggestion():
    """Test the calendar suggestion module."""
    print("\n" + "="*60)
    print("TEST: Calendar Suggestion")
    print("="*60)
    
    print("\n📧 INPUT - Scheduling Email:")
    print(f"  Text: 'Does Tuesday at 2pm work for you? Should only need 30 minutes.'")
    
    print("\n✅ EXPECTED CalendarSuggestionV1:")
    print(json.dumps(SCENARIO_3_EXPECTED_CALENDAR, indent=2, default=str))
    
    print("\n🔧 YOUR OUTPUT:")
    print("  [NOT IMPLEMENTED YET - Implement create_calendar_suggestion()]")


def run_all_tests():
    """Run all workflow tests."""
    print("\n" + "="*60)
    print("⚙️ WORKFLOW MODULE TESTS - Team C")
    print("="*60)
    
    test_priority_engine()
    test_task_generator()
    test_draft_generator()
    test_calendar_suggestion()
    
    print("\n" + "="*60)
    print("✨ Test run complete!")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
