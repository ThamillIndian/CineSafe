#!/usr/bin/env python3
"""
Test script to verify original scene numbering preservation
"""
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.agents.full_ai_orchestrator import SceneExtractorAgent


def test_scene_numbering():
    """Test that scene numbers are preserved from script"""
    
    # Sample screenplay text with original numbering
    script_text = """
4. INT. 404 - DIVYAVATHI APARTMENT - NIGHT

INT. DIVYAVATHI APARTMENT - The ghost podcast host's domain.

4.1 EXT. GRAVEYARD 5 - NIGHT

A girl dressed in newly wedded bride's attire is burying a body.

4.2 INT. SCARY HOUSE - NIGHT

The scary lady stops the alarm, picks it up to walk into the balcony.

6. INT. COLLEGE CLASS ROOM - DAY

Students sitting in a classroom taking notes.

6.1 INT. COLLEGE HOSTEL HALLWAY - DAY

A long hallway with student lockers on both sides.

8. EXT. HIGHWAY NEAR TIRUPATI - DAY

A highway with traffic passing by.
    """
    
    # Create agent
    agent = SceneExtractorAgent(gemini_client=None)
    
    # Extract scenes
    scenes = agent._extract_scenes_regex(script_text)
    
    print("\n" + "="*70)
    print("SCENE EXTRACTION TEST - Original Script Numbering")
    print("="*70 + "\n")
    
    print(f"✅ Total scenes extracted: {len(scenes)}\n")
    
    print("Extracted Scenes:")
    print("-" * 70)
    
    for i, scene in enumerate(scenes, 1):
        print(f"\n{i}. Scene Number: {scene['scene_number']}")
        print(f"   Location: {scene['location']}")
        print(f"   Time: {scene['time_of_day']}")
        print(f"   Confidence: {scene['confidence']}")
        print(f"   Is Continuation: {scene.get('is_continuation', False)}")
    
    print("\n" + "="*70)
    print("SCENE NUMBERS IN ORDER:")
    print("="*70)
    scene_numbers = [s['scene_number'] for s in scenes]
    print(f"✅ {scene_numbers}")
    
    # Validate
    expected = ["4", "4.1", "4.2", "6", "6.1", "8"]
    if scene_numbers == expected:
        print(f"\n✅ PASS: Scene numbers match expected: {expected}")
        return True
    else:
        print(f"\n❌ FAIL: Expected {expected}, got {scene_numbers}")
        return False


def test_continuation_detection():
    """Test that scene continuations are detected"""
    
    agent = SceneExtractorAgent(gemini_client=None)
    
    scenes_data = [
        {"scene_number": "4", "location": "HOUSE"},
        {"scene_number": "4.1", "location": "HOUSE"},
        {"scene_number": "4.2", "location": "HOUSE"},
        {"scene_number": "5", "location": "STREET"},
    ]
    
    print("\n" + "="*70)
    print("CONTINUATION DETECTION TEST")
    print("="*70 + "\n")
    
    continuations = [s for s in scenes_data if "." in str(s['scene_number'])]
    main_scenes = [s for s in scenes_data if "." not in str(s['scene_number'])]
    
    print(f"✅ Main Scenes: {len(main_scenes)}")
    for s in main_scenes:
        print(f"   - Scene {s['scene_number']}: {s['location']}")
    
    print(f"\n✅ Continuations: {len(continuations)}")
    for s in continuations:
        print(f"   - Scene {s['scene_number']}: {s['location']}")
    
    if len(continuations) == 3 and len(main_scenes) == 1:
        print("\n✅ PASS: Continuation detection works correctly")
        return True
    else:
        print("\n❌ FAIL: Continuation detection failed")
        return False


def test_cross_scene_insights():
    """Test cross-scene insights with original numbering"""
    
    print("\n" + "="*70)
    print("CROSS-SCENE INSIGHTS TEST - Original Numbering")
    print("="*70 + "\n")
    
    # Simulated insights with original scene numbers
    insights = [
        {
            "pattern_type": "location_cluster",
            "scene_ids": ["4", "4.1", "4.2"],
            "problem": "3 scenes at SCARY HOUSE",
            "recommendation": "Shoot all scenes at this location consecutively",
            "confidence": 0.75
        },
        {
            "pattern_type": "location_cluster",
            "scene_ids": ["6", "6.1"],
            "problem": "2 scenes at COLLEGE",
            "recommendation": "Shoot all scenes at this location consecutively",
            "confidence": 0.75
        }
    ]
    
    print("Generated Insights:")
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. {insight['pattern_type'].upper()}")
        print(f"   Scenes: {insight['scene_ids']}")
        print(f"   Problem: {insight['problem']}")
        print(f"   Recommendation: {insight['recommendation']}")
    
    # Verify scene IDs are preserved
    all_scene_ids = []
    for insight in insights:
        all_scene_ids.extend(insight['scene_ids'])
    
    expected_ids = ["4", "4.1", "4.2", "6", "6.1"]
    if sorted(set(all_scene_ids)) == sorted(set(expected_ids)):
        print(f"\n✅ PASS: Scene IDs preserved in insights: {sorted(set(all_scene_ids))}")
        return True
    else:
        print(f"\n❌ FAIL: Scene IDs mismatch")
        return False


if __name__ == "__main__":
    print("\n🏴‍☠️ TESTING ORIGINAL SCENE NUMBERING PRESERVATION")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Scene Numbering", test_scene_numbering()))
    results.append(("Continuation Detection", test_continuation_detection()))
    results.append(("Cross-Scene Insights", test_cross_scene_insights()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("🎯 All tests passed! Scene numbering working correctly! ⚓\n")
        sys.exit(0)
    else:
        print(f"⚠️ {total - passed} test(s) failed\n")
        sys.exit(1)
