# 🚀 ShootSafe AI - Quick Start Guide

## 5-Minute Setup (Docker)

### Step 1: Get Gemini API Key
```bash
# Go to https://makersuite.google.com/app/apikey
# Copy your API key
```

### Step 2: Start Docker Containers
```bash
cd /path/to/project

# Set your API key
export GEMINI_API_KEY="your-api-key-here"

# Start all services
docker-compose up -d

# Wait ~30 seconds for services to start
docker-compose ps
```

### Step 3: Check Services
```bash
# Backend API (auto-runs migrations)
curl http://localhost:8000/health

# Swagger UI
open http://localhost:8000/docs

# Celery Flower (task monitoring)
open http://localhost:5555
```

**That's it!** ✅

---

## 10-Minute Demo (What Works Now)

### 1. Create a Project
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dhoom 5",
    "language": "Hindi",
    "base_city": "Mumbai",
    "states": ["MH", "GJ"],
    "scale": "big_budget"
  }'

# Copy the project_id from response
PROJECT_ID="xxxx-xxxx-xxxx-xxxx"
```

### 2. View Datasets
The following CSV files are already loaded:
```
backend/app/datasets/data/
├── rate_card.csv                    ✅ 48 departments
├── complexity_multipliers.csv       ✅ 30 features
├── risk_weights.csv                 ✅ 20 risk types
├── city_state_multipliers.csv       ✅ 18 locations
└── location_library.csv             ✅ 35 location types
```

### 3. Test Risk Scoring (Enhancement #2)
```bash
# Create a test request with risk amplification
curl -X POST http://localhost:8000/api/v1/test-risk-scorer \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"value": "Sea Beach", "confidence": 0.95},
    "stunt_level": {"value": "heavy", "confidence": 0.90},
    "time_of_day": {"value": "night", "confidence": 0.95},
    "water_complexity": {"value": "complex", "confidence": 0.85},
    "crowd_size": {"value": "medium", "confidence": 0.80}
  }'

# Response will show:
# - Base risk scores (0-30 per pillar)
# - Amplification factor: 1.4x (Night + Water + Stunt combo!)
# - Final risk score with explanation
```

### 4. Test Budget Estimation (Enhancement #3)
```bash
# Includes confidence-based ranges
curl -X POST http://localhost:8000/api/v1/test-budget-estimator \
  -H "Content-Type: application/json" \
  -d '{
    "stunt_level": {"value": "heavy", "confidence": 0.40},
    "water_complexity": {"value": "complex", "confidence": 0.30},
    "location": {"value": "Sea Beach", "confidence": 0.95}
  }'

# Response will show:
# - Cost range: ₹XXX,XXX - ₹XXX,XXX (wide due to low confidence)
# - Line items breakdown
# - Volatility drivers (what's uncertain)
```

### 5. Test Cross-Scene Auditor (Enhancement #1)
```bash
# Coming soon in next phase
```

---

## 📂 Project Structure (What's Built)

```
✅ COMPLETE:
├── backend/app/
│   ├── config.py               ✅ Settings management
│   ├── database.py             ✅ SQLAlchemy setup
│   ├── main.py                 ✅ FastAPI app
│   ├── models/
│   │   ├── database.py         ✅ 14 database tables
│   │   └── schemas.py          ✅ Request/response models
│   ├── agents/
│   │   ├── risk_scorer.py      ✅ Enhancement #2
│   │   ├── budget_estimator.py ✅ Enhancement #3
│   │   └── cross_scene_auditor.py ✅ Enhancement #1
│   ├── datasets/
│   │   ├── loader.py           ✅ Dataset loading
│   │   └── data/               ✅ 5 CSV files
│   └── utils/
│       ├── constants.py        ✅ Risk amplifiers, enums
│       └── llm_client.py       ✅ Gemini API wrapper
├── workers/
│   └── celery_app.py           ✅ Task queue config
├── requirements.txt            ✅ Dependencies
├── Dockerfile                  ✅ Container image
└── docker-compose.yml          ✅ Local dev stack

🚧 NEXT PHASE:
├── API Endpoints (projects, upload, run, results, whatif, report)
├── Remaining Agents (scene_extractor, orchestrator, etc.)
├── Scene Parsing & Extraction
├── Database Migrations
└── Frontend (React)
```

---

## 🔧 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs backend
docker-compose logs postgres

# Rebuild containers
docker-compose down -v
docker-compose up --build
```

### Database Error
```bash
# Reset database
docker-compose exec postgres dropdb -U shootsafe shootsafe_db
docker-compose exec postgres createdb -U shootsafe shootsafe_db

# Restart backend
docker-compose restart backend
```

### Gemini API Not Working
```bash
# Check API key
echo $GEMINI_API_KEY

# Set if missing
export GEMINI_API_KEY="your-key"
docker-compose restart backend
```

### Redis Connection Failed
```bash
# Check Redis is running
docker-compose ps redis

# Restart if needed
docker-compose restart redis
```

---

## 📝 What's NOT Built Yet

These will be implemented in next phases:

- [ ] Scene parsing from PDF/DOCX
- [ ] Scene extraction via LLM
- [ ] Validation/repair agent
- [ ] Orchestrator agent
- [ ] Mitigation planner
- [ ] PDF report generation
- [ ] What-if simulator endpoint
- [ ] Frontend UI (React)
- [ ] Advanced RAG integration

---

## 🎯 Next Steps

1. **Setup Frontend** → React dashboard
2. **Implement Endpoints** → API routes for upload, run, results
3. **Build Scene Parser** → Extract scenes from PDF/DOCX
4. **Orchestrator Agent** → Run full pipeline
5. **Integration Tests** → End-to-end flows
6. **Performance Tuning** → Optimize for large scripts

---

## 📚 Key Files to Understand

| File | Purpose |
|------|---------|
| `app/config.py` | Settings from environment |
| `app/database.py` | DB initialization |
| `app/models/database.py` | SQLAlchemy models (14 tables) |
| `app/agents/risk_scorer.py` | Risk scoring with amplification |
| `app/agents/budget_estimator.py` | Budget with confidence ranges |
| `app/agents/cross_scene_auditor.py` | Project-level intelligence |
| `app/datasets/loader.py` | CSV dataset loading |
| `app/utils/constants.py` | Risk amplifiers, enums |
| `docker-compose.yml` | Service definitions |

---

## 💡 How to Extend

### Add a New Risk Amplifier
```python
# In app/utils/constants.py
RISK_AMPLIFIERS = {
    ("night_shoot", "water", "stunt"): 1.4,  # Already here
    ("new_combo1", "new_combo2"): 1.5,  # Add new combos
}
```

### Add a New Dataset
1. Create CSV in `backend/app/datasets/data/`
2. Add loader method in `backend/app/datasets/loader.py`
3. Update `validate_datasets.py` with validation rules

### Add a New Agent
1. Create file in `backend/app/agents/`
2. Implement agent class
3. Call from orchestrator

---

## 🚢 Deployment

For production deployment, see `docs/DEPLOYMENT.md`

---

## 🆘 Need Help?

- Check logs: `docker-compose logs -f service-name`
- Test database: `docker-compose exec postgres psql -U shootsafe`
- Monitor tasks: `http://localhost:5555` (Flower)
- API docs: `http://localhost:8000/docs` (Swagger)

---

**Ready to ship? Let's go!** ⚓🏴‍☠️
