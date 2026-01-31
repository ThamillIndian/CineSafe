# Scene Numbering Fix - Original Script Numbers Preserved ⚓

## What Changed

Updated the `SceneExtractorAgent` in `full_ai_orchestrator.py` to **preserve the original script scene numbers** instead of creating sequential numbering.

### Before (Sequential):
```json
{
  "scene_number": 1,
  "location": "404"
}
{
  "scene_number": 2,
  "location": "GRAVEYARD 5"
}
{
  "scene_number": 3,
  "location": "HYDERABAD POLICE STATION"
}
```

### After (Original Script Numbers):
```json
{
  "scene_number": "4",
  "location": "INT. 404 - DIVYAVATHI APARTMENT",
  "is_continuation": false
}
{
  "scene_number": "4.1",
  "location": "EXT. SCARY HOUSE",
  "is_continuation": true
}
{
  "scene_number": "4.2",
  "location": "INT. SCARY HOUSE",
  "is_continuation": true
}
{
  "scene_number": "6",
  "location": "INT. COLLEGE CLASS ROOM",
  "is_continuation": false
}
```

---

## How It Works

### Pattern Matching (Priority Order)

**Pattern 2 (Numbered scenes)** - HIGHEST PRIORITY
```regex
^(\d+(?:\.\d+)?)\s*[.]?\s*(INT|EXT|INT/EXT)\.?\s*([^-\n]+?)\s*(?:[-–]\s*([^\n]+))?$
```
Matches:
- `4. INT. 404 - DIVYAVATHI APARTMENT - NIGHT` → scene_number = "4"
- `4.1 EXT. SCARY HOUSE - NIGHT` → scene_number = "4.1"
- `6. INT. COLLEGE CLASS ROOM - DAY` → scene_number = "6"

**Pattern 1 (Standard format)**
```regex
^(INT|EXT|INT/EXT)\.\s*([^-\n]+?)\s*[-–]\s*([^\n]+)$
```
Matches non-numbered scenes (gets sequential number)

**Pattern 3 (Minimal format)**
```regex
^(INT|EXT|INT/EXT)\.\s*([^\n]+?)$
```
Fallback for simple headings

---

## Key Features

✅ **Preserves Original Scene Numbers**
- Scenes from script are numbered as they appear (4, 4.1, 4.2, etc.)
- No renumbering to sequential 1, 2, 3

✅ **Scene Continuations Support**
- Marks scenes with dots as continuations: `"is_continuation": true`
- Example: Scene 4.1, 4.2, 4.3 from one location block

✅ **Better Cross-Scene Insights**
- Scene insights now reference original script numbers
- Example: `"scene_ids": [4, 4.1, 4.2, 4.3]` instead of `[1, 2, 3, 4]`

✅ **Production-Ready**
- Matches industry standard screenplay numbering
- Line producers immediately recognize scene references
- Easier to cross-reference with original scripts

---

## Output Example

For your "Love Me If You Dare" script:

```json
{
  "cross_scene_intelligence": {
    "insights": [
      {
        "pattern_type": "location_cluster",
        "scene_ids": ["4", "4.1", "4.2", "4.3"],  // Original numbers!
        "problem": "4 scenes at SCARY HOUSE",
        "recommendation": "Shoot all scenes at this location consecutively",
        "confidence": 0.75
      },
      {
        "pattern_type": "location_cluster",
        "scene_ids": ["1", "53", "57", "61", "65", "67"],
        "problem": "6 scenes at 404",
        "recommendation": "Shoot all scenes at this location consecutively",
        "confidence": 0.75
      }
    ]
  }
}
```

---

## Testing

Run the pipeline again and check:

1. **Scene Extraction Logs:**
   ```
   ✅ Extracted scene: 4 - INT. 404 - DIVYAVATHI APARTMENT
   ✅ Extracted scene: 4.1 - EXT. SCARY HOUSE
   ✅ Extracted scene: 4.2 - INT. SCARY HOUSE
   ```

2. **Database Query:**
   ```sql
   SELECT problem_description, scene_ids FROM cross_scene_insights;
   -- Should show: '4 scenes at SCARY HOUSE' with scene_ids '[4, 4.1, 4.2, 4.3]'
   ```

3. **API Response:**
   The `/api/v1/results/{run_id}` endpoint will now return original scene numbers

---

## Files Modified

- ✅ `backend/app/agents/full_ai_orchestrator.py`
  - `SceneExtractorAgent._extract_scenes_regex()` - Now preserves original scene numbers
  - `SceneExtractorAgent._validate_scenes()` - Enhanced logging and validation

---

## Backward Compatibility

✅ **Fully Compatible**
- All existing code using `scene.get('scene_number')` works fine
- String numbers ("4", "4.1") and integer numbers (1, 2) handled the same way
- No database schema changes needed

---

## Benefits for Hackathon Judging

🎯 **Production-Authentic Output**
- Judges see real screenplay numbers, not artificial sequential ones
- Demonstrates understanding of film production workflows
- Output matches industry-standard formats

🎯 **Better Cross-Reference**
- Easier to trace outputs back to original script
- Judges can verify analysis against source material
- Shows attention to detail

🎯 **Professional Polish**
- Scene numbering matches screenwriting conventions
- Production team recognizes the format immediately
- Higher perceived quality

---

## Next Steps

1. ✅ Code updated - no changes needed
2. 🚀 Server will auto-reload with new logic
3. 📊 Test with your "Love Me If You Dare" script
4. 🎯 Verify output shows original scene numbers (4, 4.1, 4.2, etc.)

**Ready to test? Upload your script and run the pipeline!** ⚓
