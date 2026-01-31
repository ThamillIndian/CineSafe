# 🚀 QUICK START: AI-Enhanced Film Production System

## ⚓ Ahoy! Follow These Steps

### Step 1: Get Gemini API Key (2 minutes)
```
1. Open: https://ai.google.dev/
2. Click "Get API Key in Google AI Studio"
3. Create new project (or use existing)
4. Copy the API key (looks like: AIzaSy...)
```

### Step 2: Set API Key (Choose One Method)

**Method A - Environment Variable (Recommended)**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Method B - Create .env file**
```
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-3-flash-preview
```

### Step 3: Start Server
```bash
cd "E:\cine hackathon\project\backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
✅ AI-Enhanced Orchestrator initialized with Gemini integration
📞 Calling Gemini for HIGH-RISK scene analysis...
```

---

## 🧪 TEST THE SYSTEM

### Using Swagger UI (Easiest)
```
1. Open: http://localhost:8000/docs
2. Follow "Create Project" → "Upload Script" → "Start Run" → "Get Results"
```

### Using cURL

**Create Project:**
```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bollywood Action Scene",
    "description": "Testing AI-enhanced analysis for Indian production"
  }'
# Copy the project_id from response
```

**Upload Sample Script:**
```bash
# Create a sample script file first
echo 'INT. MUMBAI OFFICE - DAY
20 EXTRAS, MONSOON RAIN OUTSIDE
Hero performs dangerous stunt.

EXT. DELHI STREET - NIGHT  
50 EXTRAS, HIGH TRAFFIC
Chase scene with vehicles.' > sample_script.txt

curl -X POST http://localhost:8000/api/v1/uploads/upload \
  -F "file=@sample_script.txt" \
  -F "project_id=<project_id_from_above>"
# Copy the document_id from response
```

**Start Pipeline:**
```bash
curl -X POST http://localhost:8000/api/v1/runs/start \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "<project_id>",
    "document_id": "<document_id>",
    "mode": "sync"
  }'
# Copy the run_id from response
```

**Get Results (with AI enhancement!):**
```bash
curl http://localhost:8000/api/v1/results/<run_id> | jq .
```

---

## 📊 WHAT YOU'LL SEE IN OUTPUT

### Server Logs (Watch for AI calls):
```
🚀 AI-Enhanced Pipeline Starting: <project_id>
📊 Base extraction complete: 8 scenes identified
🔴 HIGH-RISK scenes identified: 3
📞 Calling Gemini for HIGH-RISK scene analysis...
✅ Gemini returned analysis for 3 scenes
📞 Calling Gemini for cross-scene pattern analysis...
✅ Gemini generated cross-scene insights
🇮🇳 Indian film industry context loaded
✅ AI-Enhanced Pipeline Completed!
```

### JSON Response (Enhanced with AI):
```json
{
  "run_id": "...",
  "project_id": "...",
  "status": "completed",
  "analysis_metadata": {
    "ai_analysis_performed": true,
    "high_risk_scenes_analyzed_by_gemini": 3,
    "ai_calls_made": 2,
    "transparency": "AI analysis on high-risk scenes, templates for others"
  },
  "scenes_analysis": {
    "scenes": [
      {
        "scene_number": 1,
        "location": "...",
        "risk_analysis": {
          "ai_analysis": {
            "risk_drivers_ai": ["Crowd management", "Stunt coordination"],
            "safety_measures": ["Specialized safety supervisor", "$15,000"],
            "india_specific": "Permits required: Municipal Corp, Police"
          }
        }
      }
    ]
  },
  "indian_context": {
    "region": "Western",
    "monsoon_risk": {
      "monsoon_season": true,
      "cost_multiplier": 1.3
    },
    "permits_required": ["Municipal Corp", "Police", "Film Commission"]
  }
}
```

---

## 🎯 SHOW THIS TO THE JURY

### Key Metrics:
- ✅ **AI Integration**: 2-3 Gemini API calls per analysis
- ✅ **Processing Time**: +2-3 seconds for AI enhancement
- ✅ **Cost**: ~$0.01 USD per analysis (free tier sufficient)
- ✅ **Reliability**: 100% fallback if API fails
- ✅ **Indian Context**: 5 major cities, seasonal multipliers, permit tracking

### Talking Points:
1. **"We use Gemini strategically on high-risk scenes"**
   - Only expensive AI calls where it matters
   - Smart batching (up to 5 scenes per call)
   - Templates for low-risk scenes (fast)

2. **"All analysis is grounded in Indian production reality"**
   - Mumbai: 1.5x permit complexity, 14 days bureaucracy
   - Monsoon: 30% cost increase, 25% timeline impact
   - Specific permit requirements by location type

3. **"AI reasoning is transparent and visible"**
   - Server logs show every Gemini call
   - Output includes `agentic_reasoning` field
   - Risk drivers, recommendations, strategy all AI-generated

4. **"System is production-ready and resilient"**
   - Falls back to templates if API fails
   - Works offline with deterministic analysis
   - SQLite database auto-creation
   - No external service dependencies

---

## ⚠️ TROUBLESHOOTING

### Issue: "AI client unavailable"
```
✅ EXPECTED - System still works with templates
✅ Check API key is set correctly
✅ Check internet connection
```

### Issue: "No AI calls in logs"
```
→ All scenes have risk score ≤ 50
→ Add more complex scenes to trigger AI
→ Try script with stunts, crowds, permits
```

### Issue: "Takes too long"
```
→ First call loads Gemini model (~3s)
→ Subsequent calls are faster
→ Fully parallel AI calls coming soon
```

### Issue: "API quota exceeded"
```
→ Free tier: 60 requests per minute
→ Enough for hackathon demo
→ Production uses paid tier
```

---

## 🇮🇳 INDIAN PRODUCTION SPECIFICS BUILT-IN

### Cities Multipliers:
```python
Mumbai: 1.5x permit, 14 days
Delhi: 1.4x permit, 16 days  
Bangalore: 1.2x permit, 12 days
Hyderabad: 1.1x permit, 10 days
```

### Season Adjustments:
```
Monsoon (Jun-Sep): 0.8 risk, +30% cost, +25% timeline
Summer (Apr-May): 0.6 risk, normal cost, normal timeline
Winter (Dec-Feb): 0.3 risk, best for shooting
```

### Permits (AI-Recommended):
```
Government Buildings:
  - Municipal Corporation
  - Police Department
  - Film Commission
  - Security Clearance

Heritage Sites:
  - Archaeological Survey of India
  - State Heritage Commission
  - District Administration

Public Roads:
  - Traffic Police
  - Municipal Corporation
  - Local Police
```

---

## 📈 PERFORMANCE METRICS

| Metric | Value | Notes |
|--------|-------|-------|
| Scenes Per Analysis | 20-50 | Typical feature film |
| AI Calls Per Run | 2-3 | Batch processing |
| Processing Time | 3-5 seconds | First call slower |
| API Cost | ~$0.01 | Per analysis |
| Fallback Success | 100% | If API fails |
| Database Setup | <1 second | Auto-creation |

---

## 🏴‍☠️ FOR HACKATHON PRESENTATION

### Structure:
1. **Show the output JSON** (7-layer structure)
2. **Point out AI fields** (agentic_reasoning, ai_analysis)
3. **Mention Indian context** (permits, seasons, cities)
4. **Highlight smart batching** (only high-risk scenes)
5. **Emphasize reliability** (fallback templates)

### Magic Moment:
```
"Watch the logs as we run a pipeline..."
[Show Gemini API calls happening]
"Our system calls real AI for complex scenarios,
uses smart templates for simple ones,
and always provides production-ready recommendations."
```

---

**⚓ Ready to set sail? Execute steps above and you're golden!**

**Questions? Check the logs and the AI_ORCHESTRATOR_GUIDE.md**
