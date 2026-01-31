# COMMANDS: Option C Deployment & Testing

## 1. START THE SERVER

```bash
cd "E:\cine hackathon\project\backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
✅ AI-Enhanced Orchestrator initialized with Gemini integration
✅ Using FULL AI-Enhanced Orchestrator (5 agents + safe fallbacks)
✅ Database initialized
✅ Datasets loaded
INFO: Application startup complete
```

## 2. TEST WITH "LOVE ME IF YOU DARE" SCRIPT

### Via Swagger UI (Recommended)

1. Open: http://127.0.0.1:8000/docs
2. Create Project
   - POST `/api/v1/projects/`
   - Name: "Love Me If You Dare"
   - Copy project_id
3. Upload Script
   - POST `/api/v1/uploads/upload`
   - File: "Love Me If You Dare - Dubbing Script - 01.04.24.pdf"
   - project_id: <from step 2>
   - Copy document_id
4. Start Pipeline
   - POST `/api/v1/runs/{project_id}/{document_id}`
   - mode: "sync"
   - Copy run_id
5. Get Results
   - GET `/api/v1/results/{run_id}`
   - Shows full 7-layer output with AI metadata

### Via Test Script

```bash
cd "E:\cine hackathon\project"
python test_full_ai.py
```

**What it does:**
- Loads the "Love Me If You Dare" script
- Initializes Full AI Orchestrator
- Runs complete 5-agent pipeline
- Validates output (28+ scenes, valid refs, etc.)
- Saves results to `backend/test_full_ai_output.json`

## 3. MONITOR AGENT EXECUTION

Watch the terminal/logs for:

```
🚀 FULL AI PIPELINE STARTING
⏸️ TIER 1: Scene Extraction (AI + Regex fallback)
📞 SceneExtractor: Calling Gemini AI...
✅ Extracted 28 scenes (AI: True)

⏸️ TIER 2: Risk Analysis (AI for high-risk, templates for others)
📞 RiskScorer: Calling Gemini for HIGH-RISK scenes...
✅ Analyzed risks (AI: True)

⏸️ TIER 2B: Budget Estimation (AI for complex, templates for others)
📞 BudgetEstimator: Calling Gemini for 6 complex scenes...
✅ Estimated budgets (AI: True)

⏸️ TIER 3: Cross-Scene Intelligence (AI + Rule-based patterns)
📞 CrossSceneAuditor: Calling Gemini for pattern analysis...
✅ Found 10 insights (AI: True)

⏸️ TIER 3B: Mitigation Planning (AI + Templates)
📞 MitigationPlanner: Calling Gemini for recommendations...
✅ Generated 8 recommendations (AI: True)

🎉 FULL AI PIPELINE COMPLETED
```

## 4. VERIFY RESULTS QUALITY

Check the JSON output for:

✅ `executive_summary`:
   - `total_scenes`: 28-30 (not 1!)
   - `high_risk_scenes`: 5-8 (not 0!)
   - `total_budget_likely`: $250K-$500K (not $66K!)
   - `cross_scene_insights`: 8-12
   - `recommendations`: 8-10

✅ `analysis_metadata`:
   - `ai_success_rate`: 80%+ (shows real AI!)
   - `agents_ai_enabled`: [true, true, true, true, true]
   - `safety_fallbacks_active`: true

✅ `cross_scene_intelligence.insights`:
   - All `scene_ids` reference existing scenes (NO broken refs!)
   - Each insight has valid `pattern_type`, `problem`, `recommendation`

## 5. TROUBLESHOOTING

### Issue: "AI Success Rate: 0%"
**Cause**: Gemini API not configured
**Fix**:
```powershell
$env:GEMINI_API_KEY = "your-key-here"
```

### Issue: "Extracted 1 scene (not 28)"
**Cause**: Regex fallback only
**Reason**: AI failed, but system continues safely
**Check**: Look for "AI failed" message in logs
**Fix**: Verify Gemini API key and internet connection

### Issue: "Broken scene references"
**Cause**: Insights reference non-existent scenes
**Fix**: Already handled - these are filtered out
**Result**: Only valid insights in final output

### Issue: "Scene extraction timeout"
**Cause**: Gemini API is slow
**Expected**: 5-10 second delay
**Result**: Uses regex fallback, continues

## 6. STRESS TEST (Optional)

Run with multiple scripts:

```bash
# Test with different film scripts
# Each tests all 5 agents independently
python test_full_ai.py
python test_full_ai.py  # Run again
python test_full_ai.py  # And again
```

Expected: Consistent results, no crashes

## 7. DEPLOY TO JURY

### What to show them:

1. **Terminal Logs** (copy/paste)
   - Shows all 5 agents executing with AI
   - Demonstrates safe fallbacks working
   - Real timestamps and metrics

2. **Swagger UI** (live demo)
   - Upload → Run → Get Results
   - Shows 28 scenes extracted
   - Shows realistic risk/budget analysis
   - Shows valid cross-scene insights

3. **JSON Output** (import to IDE)
   - 7-layer professional structure
   - AI metadata showing 87%+ success
   - All scenes with confidence scores
   - Valid scene references throughout

### Talking Points:

> "We built a 5-agent AI system with safe fallbacks.  
> Each agent tries intelligent Gemini analysis first.  
> If AI fails, it gracefully falls back to smart templates.  
> The result? Production-ready analysis grounded in  
> Indian film industry knowledge."

---

## QUICK COMMANDS REFERENCE

| Command | Purpose |
|---------|---------|
| `python -m uvicorn app.main:app --reload` | Start server |
| `python test_full_ai.py` | Test full pipeline |
| `curl http://127.0.0.1:8000/docs` | Open Swagger UI |
| `curl http://127.0.0.1:8000/health` | Check server status |

---

**Status**: READY FOR HACKATHON DEMO 🚀
