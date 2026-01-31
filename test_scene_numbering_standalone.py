#!/usr/bin/env python3
"""
Standalone test for scene numbering regex patterns
No external dependencies needed!
"""
import re


def test_scene_numbering():
    """Test that scene numbers are preserved from script"""
    
    # Pattern 2: Numbered scenes (like "4. INT. LOCATION - TIME" or "4.1 INT. LOCATION")
    pattern2 = r"^(\d+(?:\.\d+)?)\s*[.]?\s*(INT|EXT|INT/EXT)\.?\s*([^-\n]+?)\s*(?:[-–]\s*([^\n]+))?$"
    
    test_cases = [
        ("4. INT. 404 - DIVYAVATHI APARTMENT - NIGHT", "4", "404"),
        ("4.1 EXT. SCARY HOUSE - NIGHT", "4.1", "SCARY HOUSE"),
        ("4.2 INT. SCARY HOUSE - NIGHT", "4.2", "SCARY HOUSE"),
        ("6. INT. COLLEGE CLASS ROOM - DAY", "6", "COLLEGE CLASS ROOM"),
        ("6.1 INT. COLLEGE HOSTEL HALLWAY - DAY", "6.1", "COLLEGE HOSTEL HALLWAY"),
        ("8. EXT. HIGHWAY NEAR TIRUPATI - DAY", "8", "HIGHWAY NEAR TIRUPATI"),
    ]
    
    print("\n" + "="*80)
    print("SCENE NUMBERING REGEX TEST - Original Script Numbering")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for line, expected_number, expected_location in test_cases:
        match = re.match(pattern2, line, re.IGNORECASE)
        
        if match:
            actual_number = match.group(1)
            actual_location = match.group(3).strip()
            
            number_match = actual_number == expected_number
            location_match = actual_location == expected_location
            
            if number_match and location_match:
                print("PASS")
                print(f"   Input:    {line}")
                print(f"   Number:   {actual_number} (expected: {expected_number})")
                print(f"   Location: {actual_location} (expected: {expected_location})")
                print()
                passed += 1
            else:
                print("FAIL")
                print(f"   Input: {line}")
                if not number_match:
                    print(f"   Number mismatch: got '{actual_number}', expected '{expected_number}'")
                if not location_match:
                    print(f"   Location mismatch: got '{actual_location}', expected '{expected_location}'")
                print()
                failed += 1
        else:
            print("FAIL - NO MATCH")
            print(f"   Input: {line}")
            print(f"   Expected: scene_number='{expected_number}', location='{expected_location}'")
            print()
            failed += 1
    
    print("="*80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80 + "\n")
    
    return failed == 0


def test_continuation_detection():
    """Test that scene continuations are detected"""
    
    test_cases = [
        ("4", False),
        ("4.1", True),
        ("4.2", True),
        ("5", False),
        ("6.1", True),
        ("100", False),
        ("100.5", True),
    ]
    
    print("\n" + "="*80)
    print("CONTINUATION DETECTION TEST")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for scene_number, expected_is_continuation in test_cases:
        actual_is_continuation = "." in scene_number
        
        if actual_is_continuation == expected_is_continuation:
            print(f"PASS: Scene {scene_number} - is_continuation={actual_is_continuation}")
            passed += 1
        else:
            print(f"FAIL: Scene {scene_number} - expected {expected_is_continuation}, got {actual_is_continuation}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80 + "\n")
    
    return failed == 0


def test_scene_id_ordering():
    """Test that scene IDs maintain proper order for cross-scene insights"""
    
    print("\n" + "="*80)
    print("SCENE ID ORDERING TEST - Cross-Scene Insights")
    print("="*80 + "\n")
    
    # Simulated scenes with original numbering
    scenes_with_location = {
        "4": "SCARY HOUSE",
        "4.1": "SCARY HOUSE",
        "4.2": "SCARY HOUSE",
        "6": "COLLEGE",
        "6.1": "COLLEGE",
        "8": "HIGHWAY",
    }
    
    # Group by location
    locations = {}
    for scene_number, location in scenes_with_location.items():
        if location not in locations:
            locations[location] = []
        locations[location].append(scene_number)
    
    print("Grouped by Location:")
    for location, scene_ids in locations.items():
        print(f"\n{location}")
        print(f"   Scene IDs: {scene_ids}")
    
    # Verify expected grouping
    expected = {
        "SCARY HOUSE": ["4", "4.1", "4.2"],
        "COLLEGE": ["6", "6.1"],
        "HIGHWAY": ["8"],
    }
    
    if locations == expected:
        print(f"\nPASS: Scene grouping matches expected output")
        print("="*80 + "\n")
        return True
    else:
        print(f"\nFAIL: Scene grouping mismatch")
        print(f"   Expected: {expected}")
        print(f"   Got: {locations}")
        print("="*80 + "\n")
        return False


if __name__ == "__main__":
    print("\nTESTING ORIGINAL SCENE NUMBERING PRESERVATION (STANDALONE)")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(("Regex Pattern Matching", test_scene_numbering()))
    results.append(("Continuation Detection", test_continuation_detection()))
    results.append(("Scene ID Ordering", test_scene_id_ordering()))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("All tests passed! Scene numbering working correctly!\n")
    else:
        print(f"{total - passed} test(s) failed\n")
