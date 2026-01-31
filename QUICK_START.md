🏴‍☠️ QUICK START - GET RUNNING IN 5 MINUTES

═════════════════════════════════════════════════════════════════════════════

STEP 1: Start PostgreSQL & Redis (if not running)
────────────────────────────────────────────────

Option A - Docker (EASIEST):
   docker-compose up postgres redis -d

Option B - Manual:
   # Make sure PostgreSQL is running on localhost:5432
   # Make sure Redis is running on localhost:6379

═════════════════════════════════════════════════════════════════════════════

STEP 2: Install Dependencies (Already Done!)
────────────────────────────────────────────

   cd backend
   pip install -r requirements.txt
   
   (Should already be installed, but re-run if needed)

═════════════════════════════════════════════════════════════════════════════

STEP 3: Start FastAPI Backend
────────────────────────────────────────────

   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Expected output:
   ✅ Uvicorn running on http://0.0.0.0:8000
   ✅ Application startup complete
   ✅ "Started reloader process..."

═════════════════════════════════════════════════════════════════════════════

STEP 4: Open Swagger UI
────────────────────────────────────────────

   Browser: http://127.0.0.1:8000/docs

You should see:
   ✅ ShootSafe AI Swagger interface
   ✅ All 24 endpoints listed
   ✅ Each endpoint expandable with documentation

═════════════════════════════════════════════════════════════════════════════

STEP 5: Test the API (In Swagger UI)
────────────────────────────────────────────

5.1 CREATE PROJECT
   - Click: POST /api/v1/projects
   - Click "Try it out"
   - Paste this body:
   ```json
   {
     "name": "Inception 2",
     "base_city": "Los Angeles",
     "states": ["CA"],
     "scale": "big_budget"
   }
   ```
   - Click "Execute"
   - Copy the "id" from response (this is your project_id!)

5.2 UPLOAD SCRIPT
   - Click: POST /api/v1/projects/{project_id}/upload
   - Click "Try it out"
   - Replace {project_id} with the ID from step 5.1
   - Choose a PDF or DOCX file to upload
   - Click "Execute"
   - Copy the "document_id" from response

5.3 START PIPELINE (THE MAIN ONE!)
   - Click: POST /api/v1/runs/{project_id}/{document_id}
   - Replace both IDs with your values
   - Paste body:
   ```json
   {
     "mode": "full_analysis"
   }
   ```
   - Click "Execute"
   - Copy the "run_id" from response

5.4 CHECK STATUS
   - Click: GET /api/v1/runs/{run_id}/status
   - Replace {run_id} with your ID
   - Click "Execute" multiple times
   - Watch progress_percent go from 0 → 100%

5.5 GET RESULTS (When Status is 100%)
   - Click: GET /api/v1/results/{run_id}
   - Click "Execute"
   - See the full analysis! 🎉

═════════════════════════════════════════════════════════════════════════════

WHAT YOU'LL SEE
────────────────────────────────────────────

In Results:
   {
     "run_id": "abc-123",
     "total_scenes": 30,
     "total_budget": {
       "min": 2500000,
       "likely": 3200000,
       "max": 4200000
     },
     "risk_summary": {...},
     "scenes": [{...}, {...}],
     "cross_scene_insights": [{...}, {...}],
     "generated_at": "2024-01-31T12:00:00"
   }

═════════════════════════════════════════════════════════════════════════════

OPTIONAL: Try What-If Scenarios
────────────────────────────────────────────

   - Click: POST /api/v1/whatif/{run_id}
   - Paste body:
   ```json
   {
     "changes": [
       {
         "scene_id": "scene-5",
         "field": "stunt_level",
         "new_value": "high"
       }
     ]
   }
   ```
   - Click "Execute"
   - See impact: cost_delta, risk_delta, etc.

═════════════════════════════════════════════════════════════════════════════

OPTIONAL: Generate PDF Report
────────────────────────────────────────────

   - Click: POST /api/v1/reports/{run_id}/generate
   - Click "Execute"
   - See: download_url in response

   - Click: GET /api/v1/reports/{run_id}/download
   - Click "Execute"
   - Download the PDF!

═════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING
────────────────────────────────────────────

❌ "Connection refused" on startup?
   → Make sure PostgreSQL is running: docker-compose up postgres -d

❌ "No module named 'app'"?
   → Make sure you're in the backend directory: cd backend

❌ Port 8000 already in use?
   → Use different port: uvicorn app.main:app --port 8001

❌ Database errors?
   → Try: python -m alembic upgrade head
   → Or restart: docker-compose restart postgres

❌ Endpoints not showing in docs?
   → Refresh browser (Ctrl+Shift+R for hard refresh)

═════════════════════════════════════════════════════════════════════════════

FILE LOCATIONS
────────────────────────────────────────────

Project Root:
   E:\cine hackathon\project\

Backend:
   E:\cine hackathon\project\backend\

API Routers:
   E:\cine hackathon\project\backend\app\api\v1\
      ├─ projects.py
      ├─ uploads.py
      ├─ runs.py
      ├─ results.py
      ├─ whatif.py
      └─ reports.py

Main App:
   E:\cine hackathon\project\backend\app\main.py

Celery Tasks:
   E:\cine hackathon\project\backend\workers\tasks.py

═════════════════════════════════════════════════════════════════════════════

API DOCUMENTATION
────────────────────────────────────────────

All endpoints have:
   ✅ Full docstrings
   ✅ Parameter descriptions
   ✅ Response schemas
   ✅ Example requests/responses
   ✅ Error handling

Accessible via:
   http://127.0.0.1:8000/docs (Swagger UI)
   http://127.0.0.1:8000/redoc (ReDoc)

═════════════════════════════════════════════════════════════════════════════

🎯 DEMO SCRIPT FOR JUDGES
────────────────────────────────────────────

"Let me show you our intelligent film production system:

1. First, I'll create a project
   [POST /projects] → Shows project created ✅

2. Upload a screenplay
   [POST /upload] → Extract text from PDF ✅

3. Start the intelligent analysis pipeline
   [POST /runs] → Explain: 5 AI agents start working!
              CrewAI coordinates them hierarchically
              MCP allows tool sharing between agents

4. Watch real-time progress
   [GET /status] → Progress: 25%, Extracting scenes
              → Progress: 50%, Analyzing risks
              → Progress: 75%, Calculating budgets
              → Progress: 100%, Complete! ✅

5. Get comprehensive analysis
   [GET /results] → Shows:
              * 30 scenes extracted
              * Risk scores (Safety, Logistics, Schedule, Budget, Compliance)
              * Budget range: $2.5M - $4.2M
              * 7 cross-scene insights (location chains, fatigue clusters, etc.)
              * Producer summary

6. Try what-if scenarios
   [POST /whatif] → Change scene parameters
              → Get instant impact analysis
              → Cost: +$125K, Risk: +15 points

7. Generate professional report
   [POST /reports/generate] → PDF created
   [GET /reports/download] → Download PDF

That's our system: Intelligent agents analyzing film productions!"

═════════════════════════════════════════════════════════════════════════════

🏴‍☠️ YOU'RE READY!

Start with: cd backend && uvicorn app.main:app --reload

Then visit: http://127.0.0.1:8000/docs

Show the jury the magic! 🚀

═════════════════════════════════════════════════════════════════════════════
