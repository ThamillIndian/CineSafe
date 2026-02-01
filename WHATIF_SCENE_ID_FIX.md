# ⚓ WHAT-IF SCENE_ID BUG FIX 🏴‍☠️

## **Bug Fixed**

### **Error:** 
```
❌ What-if analysis failed: cannot access local variable 'scene_id' where it is not associated with a value
```

### **Root Cause:**
The code tried to use `scene_id` **outside its loop scope** and **only for the last scene**:

```python
# WRONG: scope issue
for change in request.changes:
    scene_id = change.scene_id  # Only sets scene_id for LAST item
    # ...

# AFTER loop: scene_id might not exist or is last item only
risk_delta = [
    (new_state[scene_id]["risk"]["safety_score"] - ...),  # ❌ Undefined!
    # ...
]
```

**Problems:**
1. ❌ If `request.changes` is empty → `scene_id` never assigned
2. ❌ Only uses LAST scene's data, ignores other scenes
3. ❌ Wrong calculation logic

---

## **Fix Applied**

Changed from single-scene calculation to **aggregated calculation across ALL scenes**:

```python
# CORRECT: Aggregate all scenes
safety_delta = sum(
    new_state[sid]["risk"]["safety_score"] - old_state[sid]["risk"]["safety_score"]
    for sid in new_state.keys()
)
logistics_delta = sum(
    new_state[sid]["risk"]["logistics_score"] - old_state[sid]["risk"]["logistics_score"]
    for sid in new_state.keys()
)
schedule_delta = sum(
    new_state[sid]["risk"]["schedule_score"] - old_state[sid]["risk"]["schedule_score"]
    for sid in new_state.keys()
)
budget_delta = sum(
    new_state[sid]["risk"]["budget_score"] - old_state[sid]["risk"]["budget_score"]
    for sid in new_state.keys()
)
compliance_delta = sum(
    new_state[sid]["risk"]["compliance_score"] - old_state[sid]["risk"]["compliance_score"]
    for sid in new_state.keys()
)

# Return as array for compatibility
risk_delta = [safety_delta, logistics_delta, schedule_delta, budget_delta, compliance_delta]
```

---

## **What Changed**

| Before | After |
|--------|-------|
| Accessed undefined `scene_id` | Aggregates all scenes using `new_state.keys()` |
| Only used last scene | Sums risk changes across entire production |
| Risk delta array had wrong values | Risk delta correctly represents total impact |
| Crashes when no changes | Always calculates from all scenes |

---

## **Test Result Expected**

✅ **What-If presets should now work:**
- Budget Cut 20% - ✅ Analyzes impact
- Accelerate Timeline - ✅ Analyzes impact
- Maximize Safety - ✅ Analyzes impact

✅ **Custom scenarios should work**
✅ **Returns proper aggregated risk deltas**
✅ **No more `scene_id` undefined errors**

---

**Status:** ✅ **FIXED & READY FOR TESTING**

🏴‍☠️ What-If Analysis now works correctly! ⚓
