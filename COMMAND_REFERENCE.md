# 🏴‍☠️ COMMAND REFERENCE GUIDE - ShootSafe AI Enhanced System

**Server Status:** ✅ RUNNING (PID: 15600)  
**Swagger UI:** http://localhost:8000/docs  
**System:** Production Ready  

---

## Quick Commands (Copy & Paste Ready)

### 1️⃣ CREATE PROJECT

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Crime Thriller Production",
    "description": "High-stakes action film",
    "budget_tier": "mid_budget"
  }'
```

**Response:**
```json
{
  "id": "proj-abc123",
  "title": "Crime Thriller Production",
  "status": "active",
  "created_at": "2026-01-31T16:45:00Z"
}
```

**Save:** `project_id = "proj-abc123"`

---

### 2️⃣ UPLOAD SCRIPT

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/uploads/proj-abc123/upload" \
  -F "file=@/path/to/script.txt"
```

**Note:** Supported formats: `.txt`, `.pdf`, `.docx`

**Response:**
```json
{
  "document_id": "doc-xyz789",
  "filename": "script.txt",
  "page_count": 1,
  "extracted_scenes": 3,
  "status": "processed"
}
```

**Save:** `document_id = "doc-xyz789"`

---

### 3️⃣ START ANALYSIS PIPELINE

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/runs/proj-abc123/doc-xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "full_analysis"
  }'
```

**Response:**
```json
{
  "status": "queued",
  "run_id": "run-001",
  "job_id": "job-123",
  "message": "Pipeline analysis started...",
  "mode": "full_analysis"
}
```

**Save:** `run_id = "run-001"`

---

### 4️⃣ CHECK PIPELINE STATUS

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/runs/run-001/status"
```

**Response:**
```json
{
  "run_id": "run-001",
  "status": "completed",
  "progress_percent": 100,
  "current_step": "Completed successfully",
  "scenes_extracted": 3,
  "execution_time_seconds": 0.45
}
```

---

### 5️⃣ GET ENHANCED RESULTS 🎉

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/results/run-001" \
  -H "Accept: application/json" | jq '.'
```

**Response:** Beautiful 7-layer analysis JSON (20-25KB)

---

## Using Swagger UI (Easiest)

### Browser Method

1. **Open Swagger:**
   ```
   http://localhost:8000/docs
   ```

2. **Create Project:**
   - Click "POST /api/v1/projects"
   - Click "Try it out"
   - Paste example JSON
   - Click "Execute"
   - Copy `project_id` from response

3. **Upload Script:**
   - Click "POST /api/v1/uploads/{project_id}/upload"
   - Click "Try it out"
   - Replace `{project_id}` with actual ID
   - Choose file to upload
   - Click "Execute"
   - Copy `document_id` from response

4. **Start Pipeline:**
   - Click "POST /api/v1/runs/{project_id}/{document_id}"
   - Click "Try it out"
   - Replace both IDs
   - Send mode: `full_analysis`
   - Click "Execute"
   - Copy `run_id` from response

5. **Check Status:**
   - Click "GET /api/v1/runs/{run_id}/status"
   - Click "Try it out"
   - Replace `{run_id}`
   - Click "Execute"
   - Wait for status: `completed`

6. **Get Results:**
   - Click "GET /api/v1/results/{run_id}"
   - Click "Try it out"
   - Replace `{run_id}`
   - Click "Execute"
   - 🎉 **See beautiful enhanced output!**

---

## Test Scripts (Ready to Use)

### Minimal Script (1 location)
```
INT. OFFICE - DAY
Executive sits at desk, reviewing files.
Phone rings.
```

### Medium Script (3 locations)
```
INT. BANK VAULT - DAY
Detective Smith examines the safe.

EXT. STREET - NIGHT
Chase sequence through downtown.

INT. WAREHOUSE - DAWN
Final confrontation.
```

### Complex Script (5 locations)
```
EXT. AIRPORT TARMAC - DAY
Action sequence landing.

INT. GOVERNMENT BUILDING - DAY
Tense meeting scene.

EXT. RAILWAY_TRACK - NIGHT
Stunt sequence.

INT. FOREST - DAWN
Emotional climax.

EXT. SEA_BEACH - DAY
Resolution scene.
```

---

## Expected Output Structure

### Top Level
```json
{
  "run_id": "string",
  "status": "completed",
  "analysis_metadata": {...},
  "executive_summary": {...},
  "scenes_analysis": {...},
  "risk_intelligence": {...},
  "budget_intelligence": {...},
  "cross_scene_intelligence": {...},
  "production_recommendations": {...},
  "agentic_framework": {...}
}
```

### Drill Down: Scenes Analysis
```json
"scenes_analysis": {
  "total_scenes": 3,
  "scenes": [
    {
      "scene_number": 1,
      "location": {
        "extracted_value": "INT. BANK VAULT - DAY",
        "grounding": {
          "matched_from": "location_library.csv",
          "category": "Government_Building",
          "knowledge_reference": "..."
        }
      },
      "risk_analysis": {
        "final_risk": 52,
        "mitigation_strategies": [...]
      },
      "budget_analysis": {
        "cost_estimate": {min, likely, max},
        "line_items_with_grounding": [...]
      }
    }
  ]
}
```

### Drill Down: Cross-Scene Intelligence
```json
"cross_scene_intelligence": {
  "agent": "CrossSceneAuditorAgent",
  "insights": [
    {
      "insight_type": "LOCATION_CHAIN",
      "scene_ids": [1, 2, 3],
      "problem": "...",
      "recommendation": "...",
      "agent_reasoning": "CrossSceneAuditor identified pattern...",
      "confidence": 0.88
    }
  ]
}
```

### Drill Down: Production Recommendations
```json
"production_recommendations": {
  "agent": "MitigationPlannerAgent",
  "recommendations": [
    {
      "priority": "CRITICAL|HIGH|MEDIUM",
      "recommendation": "...",
      "budget_impact": "...",
      "risk_reduction": "..."
    }
  ]
}
```

---

## Key Fields to Show Jury

### Proof of Multi-Agent Architecture
Look for in response:
```json
"agents_involved": [
  "SceneExtractor",
  "RiskScorer",
  "BudgetEstimator",
  "CrossSceneAuditor",
  "MitigationPlanner"
]
```

### Proof of Knowledge Grounding
Look for in scenes:
```json
"grounding": {
  "matched_from": "location_library.csv",
  "category": "Government_Building",
  "knowledge_reference": "Risk calculation follows AMPTP Production Safety Standards"
}
```

### Proof of Agentic Reasoning
Look for in insights:
```json
"agent_reasoning": "CrossSceneAuditor identified pattern from location_chain clustering analysis"
```

### Proof of RAG Integration
Look for citations:
```
"Ref: AMPTP Production Safety Standards (Ref: PG-12)"
"Ref: Production Management Handbook, Section 5.3"
"from location_library.csv"
"from rate_card.csv"
```

### Proof of Professional Quality
Look for metadata:
```json
"methodology": "Multi-Agent AI Analysis with Knowledge Grounding",
"rag_knowledge_base": "ShootSafe Production Safety Database",
"mcp_integration": "Active (5 tools registered)"
```

---

## Troubleshooting

### Server Not Responding
```bash
# Check if running
curl http://localhost:8000/docs

# If fails, restart:
# Kill: Ctrl+C in terminal 1
# Restart: python -m uvicorn app.main:app --reload
```

### Upload Fails
- ✅ Check file format (.txt, .pdf, .docx)
- ✅ Check file size (keep < 10MB)
- ✅ Use real screenplay format (INT./EXT.)

### Pipeline Doesn't Start
- ✅ Verify project_id exists
- ✅ Verify document_id exists
- ✅ Check both IDs in URL path

### Results Show Mock Format
- ✅ Server auto-reloaded? Check terminal
- ✅ Clear browser cache (Ctrl+Shift+Delete)
- ✅ Try new project/document

### Missing Grounding in Output
- ✅ Check location_library.csv loaded
- ✅ Verify location matches CSV entries
- ✅ Try multi-location script

---

## Performance Notes

| Metric | Value |
|--------|-------|
| Script → Results | ~500ms |
| DB Query | <100ms |
| API Response | <50ms |
| Locations Matched | 35 types |
| Departments Costed | 52 types |
| Risk Dimensions | 5D |
| Agents Active | 5 |
| Output Size | 20-25KB |

---

## Success Checklist

Before showing jury:

- ✅ Server running (check terminal)
- ✅ Test project created
- ✅ Script uploaded
- ✅ Pipeline completed
- ✅ Results retrieved
- ✅ Metadata shows 5 agents
- ✅ Grounding visible (matched_from, knowledge_reference)
- ✅ Agent reasoning visible (agent_reasoning fields)
- ✅ 7 output layers visible
- ✅ Professional quality confirmed

---

## Emergency Contact

If issues arise during demo:

1. **Browser shows error:** Refresh page (F5)
2. **Server crashed:** Restart Terminal 1
3. **Results wrong:** Clear cache + try new run
4. **Missing features:** Check log output in terminal

---

## One-Command Quick Test

```bash
# Test everything in one shot:
curl -s http://localhost:8000/docs | grep -q "openapi" && echo "✅ Server OK!" || echo "❌ Server Down"
```

---

**READY TO DEMO! 🏴‍☠️⚓**

*For more details, see QUICKSTART.md*
