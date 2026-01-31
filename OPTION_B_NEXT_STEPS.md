# Next Steps - Option B Ready to Test 🏴‍☠️

## IMMEDIATE ACTIONS

### 1️⃣ Start the Server
```bash
cd "E:\cine hackathon\project\backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
✅ Database initialized
✅ Datasets loaded
✅ Gemini client initialized  
✅ Using FULL AI-Enhanced Orchestrator (5 agents)
✅ Startup complete - API ready!
```

### 2️⃣ Access Swagger UI
```
Open in browser: http://127.0.0.1:8000/docs
```

### 3️⃣ Test the 3-Step Workflow

#### **STEP 1: Upload Script**
- Endpoint: `POST /api/v1/scripts/upload`
- Click "Try it out"
- Select a PDF or DOCX file (test script provided)
- Execute
- **Copy the `document_id` from response**

#### **STEP 2: Start Analysis**
- Endpoint: `POST /api/v1/runs/{document_id}/start`
- Click "Try it out"
- Paste the `document_id` you copied
- Execute
- **Wait for completion** (should say "completed" in response)
- **Copy the `run_id` from response**

#### **STEP 3: Get Results**
- Endpoint: `GET /api/v1/results/{run_id}`
- Click "Try it out"
- Paste the `run_id` you copied
- Execute
- **See the full 7-layer analysis output!**

---

## What to Look For ✅

### In Upload Response:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "script.pdf",
  "page_count": 42
}
```
✅ No `project_id` - that's expected and correct!

### In Start Run Response:
```json
{
  "run_id": "660f9511-f30c-52e5-b827-557766551111",
  "status": "completed",  // Or "running"
  "started_at": "...",
  "completed_at": "..."
}
```
✅ Only `document_id`, no `project_id` - perfect!

### In Results Response:
```json
{
  "run_id": "660f9511-f30c-52e5-b827-557766551111",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",  // This is document_id
  "total_scenes": 20,
  "scenes": [...],
  "cross_scene_insights": [...],
  "...": "full 7-layer output"
}
```
✅ All analysis complete and stored!

---

## Verification Checklist 🧪

Run through these checks:

### Server Health ✅
- [ ] Server starts without errors
- [ ] Database initializes
- [ ] Datasets load successfully
- [ ] Gemini client initialized
- [ ] Go to `/health` endpoint returns `{"status": "ok"}`

### Database Schema ✅
- [ ] No errors about missing columns
- [ ] No errors about foreign keys
- [ ] Tables created automatically
- [ ] New schema (no project_id in Document/Run)

### Upload Functionality ✅
- [ ] Can upload PDF files
- [ ] Can upload DOCX files  
- [ ] File size validation works (<100MB)
- [ ] Returns valid document_id
- [ ] No "project_id" in response

### Analysis Pipeline ✅
- [ ] Analysis starts immediately after upload
- [ ] Run status transitions: queued → running → completed
- [ ] No errors in orchestrator
- [ ] All 5 AI agents execute successfully
- [ ] Results stored in database

### Results Quality ✅
- [ ] Returns 7-layer output
- [ ] Scenes extracted correctly
- [ ] Risk scores calculated
- [ ] Budget estimates provided
- [ ] Cross-scene insights generated
- [ ] Recommendations included
- [ ] AI reasoning visible

---

## Common Issues & Fixes 🔧

### Issue: "ModuleNotFoundError: No module named 'projects'"
**Fix:** This is expected - projects module was deleted. Check that:
- ✅ imports in main.py don't reference projects
- ✅ Only 5 routers are imported (uploads, runs, results, whatif, reports)

### Issue: "UNIQUE constraint failed"
**Fix:** Delete database and restart:
```bash
cd backend
Remove-Item -Path "shootsafe.db" -Force
# Restart server - database auto-creates
```

### Issue: "document_id not found"
**Fix:** Make sure you're:
- ✅ Copying the EXACT document_id from upload response
- ✅ Using it in the next run endpoint
- ✅ Waiting for upload to complete before starting run

### Issue: "Run is still queued/running"
**Fix:** This is normal - analysis takes time:
- ✅ PDF parsing: ~2 sec
- ✅ AI analysis: ~10-30 sec
- ✅ Total: ~15-35 sec
- ✅ Wait and check status again

### Issue: "FileResponse import error"
**Fix:** Already fixed in uploads.py - should not occur

---

## Testing with Real Scripts 📚

### Provided Test File:
```
Location: E:\cine hackathon\project\Love Me If You Dare - Dubbing Script - 01.04.24 (1).pdf
```

**To Test:**
1. Upload this file
2. It has 1,871 lines of content
3. Should extract ~42 pages
4. Will generate 20+ scenes
5. Should show realistic analysis

---

## Performance Notes ⏱️

**Typical Timeline:**
```
0s    → Upload starts
2s    → Text extraction complete
3s    → Run created
4s    → AI pipeline starts
     
10-30s → Gemini API calls (Scene extraction, Risk scoring)
20-40s → Budget estimation
30-50s → Cross-scene analysis
40-60s → Results stored

Total: ~45-65 seconds for full analysis
```

**Bottleneck:** Gemini API calls (this is expected!)

---

## Comparison: Before vs After Testing

### Before (Old Workflow - 4 Steps):
```
1. Create project (fill form)
2. Upload script to project
3. Start run with project+document
4. Get results
```
❌ Slower, more clicks

### After (New Workflow - 3 Steps):
```
1. Upload script (1 click)
2. Start run (1 click)
3. Get results (1 click)
```
✅ Faster, simpler!

---

## Success Scenario 🏆

**When working correctly:**
1. Upload button → `document_id` returned instantly
2. Start run → Status shows "completed" within 45-60 seconds
3. Results → Full 7-layer JSON with all analysis
4. No errors, no project mentions, smooth flow

---

## Troubleshooting Guide 🔍

### If Server Won't Start:
```bash
# Check Python version (need 3.8+)
python --version

# Check dependencies
pip install -r requirements.txt

# Try starting with logging
python -m uvicorn app.main:app --log-level debug
```

### If Database Issues:
```bash
# Delete corrupted database
Remove-Item -Path "backend/shootsafe.db" -Force

# Verify SQLAlchemy
pip install sqlalchemy --upgrade
```

### If API Endpoints Missing:
```bash
# Check imports in main.py
# Should have: uploads, runs, results, whatif, reports
# Should NOT have: projects

# Restart server
```

### If Analysis Fails:
```bash
# Check Gemini API key
echo $env:GOOGLE_API_KEY

# Check orchestrator logs
# Look for: "Using FULL AI-Enhanced Orchestrator"
```

---

## Quick Reference Commands 🚀

```bash
# Start server
cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Health check
curl http://127.0.0.1:8000/health

# Swagger UI
start http://127.0.0.1:8000/docs

# ReDoc
start http://127.0.0.1:8000/redoc

# Delete DB
Remove-Item -Path "backend/shootsafe.db" -Force
```

---

## Communication for Jury 💬

**When presenting Option B, say:**

*"We've optimized the workflow for maximum efficiency. Users can now:*
1. *Upload a film script directly*
2. *Click 'Analyze'*
3. *Instantly see complete production safety and budget analysis*

*Our system eliminates unnecessary configuration steps and focuses on delivering actionable intelligence quickly. The 7-layer analysis includes scene extraction, risk scoring, budget estimation, cross-scene insights, and AI-powered recommendations - all automatically generated from the script."*

---

## Checklist Before Demo 📋

- [ ] Server running and healthy
- [ ] Can upload test script successfully  
- [ ] Analysis completes in <60 seconds
- [ ] Results show all 7 layers
- [ ] No errors in logs
- [ ] Swagger UI working
- [ ] All endpoints responding
- [ ] No "project_id" references (expected!)
- [ ] Database persisting data
- [ ] Ready to impress judges! 🏆

---

## You're Ready! 🚀

Everything is set up. Just:

1. ✅ Start the server
2. ✅ Test the workflow
3. ✅ Verify results  
4. ✅ Prepare your pitch

**Good luck with the hackathon, matey!** 🏴‍☠️

The voyage begins! ⚓
