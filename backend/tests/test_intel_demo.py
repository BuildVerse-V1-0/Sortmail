"""
Test Runner for Intelligence Module — Team B
=============================================
Run this to verify your intelligence implementations work correctly.
"""

import sys
sys.path.insert(0, '..')

from datetime import datetime
from typing import Dict, Any
import json

# Import demo data
from demo_data import (
    SCENARIO_1_RAW_EMAIL,
    SCENARIO_1_EXPECTED_INTEL,
    SCENARIO_2_RAW_EMAIL, 
    SCENARIO_2_EXPECTED_INTEL,
    SCENARIO_3_RAW_EMAIL,
    SCENARIO_3_EXPECTED_INTEL
)

# Import your implementations (uncomment as you implement)
# from core.intelligence.summarizer import summarize_thread
# from core.intelligence.intent_classifier import classify_intent
# from core.intelligence.deadline_extractor import extract_deadlines
# from core.intelligence.email_intel import analyze_thread


def test_summarizer():
    """Test the summarization module."""
    print("\n" + "="*60)
    print("TEST: Summarizer")
    print("="*60)
    
    # Input
    print("\n📧 INPUT - Email Thread:")
    print(f"  Subject: {SCENARIO_1_RAW_EMAIL['subject']}")
    print(f"  Messages: {len(SCENARIO_1_RAW_EMAIL['messages'])}")
    
    # Expected
    print("\n✅ EXPECTED OUTPUT:")
    print(f"  Summary: {SCENARIO_1_EXPECTED_INTEL['summary']}")
    
    # Your output
    print("\n🔧 YOUR OUTPUT:")
    # Uncomment when implemented:
    # result = summarize_thread(SCENARIO_1_RAW_EMAIL['messages'])
    # print(f"  Summary: {result}")
    print("  [NOT IMPLEMENTED YET - Implement summarize_thread()]")
    
    print("\n📋 CHECKLIST:")
    print("  □ Summary is 2-3 sentences")
    print("  □ Mentions the sender (Sarah)")
    print("  □ Mentions the deadline (Friday EOD)")
    print("  □ Mentions the main ask (approval)")


def test_intent_classifier():
    """Test the intent classification module."""
    print("\n" + "="*60)
    print("TEST: Intent Classifier")
    print("="*60)
    
    test_cases = [
        ("Contract Review", SCENARIO_1_RAW_EMAIL, "ACTION_REQUIRED"),
        ("FYI Notes", SCENARIO_2_RAW_EMAIL, "FYI"),
        ("Meeting Request", SCENARIO_3_RAW_EMAIL, "SCHEDULING"),
    ]
    
    for name, email, expected_intent in test_cases:
        print(f"\n📧 {name}:")
        print(f"  Subject: {email['subject']}")
        print(f"  ✅ Expected Intent: {expected_intent}")
        # Uncomment when implemented:
        # result = classify_intent(email['messages'][-1]['body_text'])
        # print(f"  🔧 Your Intent: {result}")
        print(f"  🔧 Your Intent: [NOT IMPLEMENTED]")


def test_deadline_extractor():
    """Test the deadline extraction module."""
    print("\n" + "="*60)
    print("TEST: Deadline Extractor")
    print("="*60)
    
    # Input
    text = SCENARIO_1_RAW_EMAIL['messages'][0]['body_text']
    print("\n📧 INPUT TEXT:")
    print(f"  '{text[:100]}...'")
    
    # Expected
    print("\n✅ EXPECTED DEADLINES:")
    for deadline in SCENARIO_1_EXPECTED_INTEL['extracted_deadlines']:
        print(f"  - {deadline['deadline']} (confidence: {deadline['confidence']})")
        print(f"    Source: '{deadline['source_text']}'")
    
    # Your output
    print("\n🔧 YOUR OUTPUT:")
    # Uncomment when implemented:
    # result = extract_deadlines(text)
    # for d in result:
    #     print(f"  - {d}")
    print("  [NOT IMPLEMENTED YET - Implement extract_deadlines()]")


def test_full_pipeline():
    """Test the complete intelligence pipeline."""
    print("\n" + "="*60)
    print("TEST: Full Intelligence Pipeline")
    print("="*60)
    
    print("\n📧 INPUT: Scenario 1 - Contract Review")
    print(f"  Thread ID: {SCENARIO_1_RAW_EMAIL['thread_id']}")
    
    print("\n✅ EXPECTED ThreadIntelV1:")
    print(json.dumps(SCENARIO_1_EXPECTED_INTEL, indent=2, default=str))
    
    print("\n🔧 YOUR OUTPUT:")
    # Uncomment when implemented:
    # from contracts.ingestion import EmailThreadV1
    # thread = EmailThreadV1(**SCENARIO_1_RAW_EMAIL)
    # result = analyze_thread(thread)
    # print(json.dumps(result.dict(), indent=2, default=str))
    print("  [NOT IMPLEMENTED YET - Implement analyze_thread()]")


def run_all_tests():
    """Run all intelligence tests."""
    print("\n" + "="*60)
    print("🧠 INTELLIGENCE MODULE TESTS - Team B")
    print("="*60)
    
    test_summarizer()
    test_intent_classifier()
    test_deadline_extractor()
    test_full_pipeline()
    
    print("\n" + "="*60)
    print("✨ Test run complete!")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
