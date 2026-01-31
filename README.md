# 🎬 ShootSafe AI - Film Production Safety & Budgeting System

An intelligent, agent-based system that analyzes film scripts for production risks, budgets, and logistics using LLM-powered agents with human-like decision-making.

## 🌟 Key Features

### **End-to-End Workflow**
1. **Upload Script** → PDF/DOCX → Automatic text extraction
2. **Extract Scenes** → Parse into structured scene blocks
3. **Analyze Intelligently** → 8 specialized agents extract facts + risks + budget
4. **Dashboard** → Scene breakdown, risk charts, budget ranges, mitigations
5. **What-If Simulation** → Instant scenario testing (no LLM!)
6. **Download PDF** → Professional report with all analysis

### **3 Key Enhancements (Hackathon Focus)**

**Enhancement #1: Cross-Scene Intelligence** 🔍
- Project-level inefficiency detection
- Finds location chains, fatigue clusters, resource bottlenecks
- Recommends optimal shoot order

**Enhancement #2: Risk Amplification** ⚠️
- Detects dangerous feature combinations
- Night + Water + Stunts = 1.4x risk amplification
- Explainable risk scoring

**Enhancement #3: Confidence & Uncertainty** 📊
- Every field gets confidence score
- Budget ranges (min/likely/max) based on uncertainty
- Producer can clarify low-confidence fields

## 🏗️ Architecture

```
Frontend (React)
    ↓
FastAPI Backend (Python)
    ↓
Celery Workers (8 Specialized Agents)
    ↓
├─ PostgreSQL (Data)
├─ Redis (Queue)
├─ Qdrant (RAG Vector DB)
└─ Gemini API (LLM)
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/v1/              # FastAPI endpoints
│   ├── agents/              # 8 agent modules
│   │   ├── orchestrator.py  # Supervisor
│   │   ├── scene_extractor.py
│   │   ├── risk_scorer.py        # Enhancement #2
│   │   ├── budget_estimator.py   # Enhancement #3
│   │   ├── cross_scene_auditor.py # Enhancement #1
│   │   └── ...
│   ├── datasets/
│   │   └── data/            # 5 CSV files (rate cards, multipliers, etc.)
│   ├── models/
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── utils/               # Helpers, constants, LLM client
│   └── main.py             # FastAPI app entry
├── workers/
│   ├── celery_app.py        # Celery config
│   └── tasks.py             # Celery tasks
├── requirements.txt
├── Dockerfile
└── docker-compose.yml       # Local development setup

frontend/                     # React app (separate)
docs/                        # API docs, guides
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (recommended)
- Gemini API key
- PostgreSQL 15 (or use Docker)

### Option 1: Docker (Recommended)

```bash
# 1. Set environment
export GEMINI_API_KEY="your_key_here"

# 2. Start services
docker-compose up -d

# 3. Wait for services to be healthy
docker-compose ps

# 4. Access the app
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Celery Flower: http://localhost:5555
```

### Option 2: Local Development

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start PostgreSQL & Redis separately (or use Docker just for those)
docker-compose up postgres redis qdrant -d

# 3. Set environment
export DATABASE_URL="postgresql://shootsafe:shootsafe@localhost:5432/shootsafe_db"
export REDIS_URL="redis://localhost:6379/0"
export GEMINI_API_KEY="your_key_here"

# 4. Run migrations
alembic upgrade head

# 5. Start API (terminal 1)
uvicorn app.main:app --reload

# 6. Start Celery worker (terminal 2)
celery -A workers.celery_app worker --loglevel=info

# 7. Start Flower (terminal 3, optional)
celery -A workers.celery_app flower
```

## 📊 Database

**Core Tables:**
- `projects` → Project metadata
- `documents` → Uploaded scripts
- `runs` → Pipeline executions (versioning)
- `scenes` → Parsed scenes
- `scene_extractions` → LLM extraction output with confidence
- `scene_risks` → Risk scores (includes amplification)
- `scene_costs` → Budget estimates (includes ranges)
- `cross_scene_insights` → Project-level inefficiencies
- `project_summaries` → Aggregated results JSON
- `jobs` → Worker task tracking
- `decisions` → Producer edits/what-ifs
- `assumptions` → Locked constraints

## 📊 Datasets (The Deterministic Brain)

5 CSV files in `backend/app/datasets/data/`:

1. **rate_card.csv** → Department costs by scale
2. **city_state_multipliers.csv** → Regional cost/permit/logistics multipliers
3. **complexity_multipliers.csv** → Scene feature → cost/risk multipliers
4. **risk_weights.csv** → Feature → risk pillar points (0-30 each)
5. **location_library.csv** → Location type → permit tier, complexity

**Why CSV files?**
- Deterministic (no hallucination)
- Reproducible (same input = same output)
- Auditable (producer can see exactly how number was calculated)
- Easy to update (no code changes needed)

## 🤖 The 8 Agents

| # | Agent | Input | Output | Type |
|---|-------|-------|--------|------|
| 0 | **Orchestrator** | Job request | Pipeline execution | Supervisor |
| 1 | **Scene Splitter** | Raw text | Scene blocks | Code |
| 2 | **Scene Extractor** | Scene text | JSON + evidence + confidence | LLM |
| 3 | **Validator/Repair** | Broken extraction | Fixed JSON | LLM |
| 4 | **Risk Scorer** | Features | Scores + amplification | Code (Enh #2) |
| 5 | **Budget Estimator** | Features + confidence | Min/likely/max ranges | Code (Enh #3) |
| 6 | **Cross-Scene Auditor** | All scenes | Project insights | LLM (Enh #1) |
| 7 | **Mitigation Planner** | Risks + RAG | Checklists + recommendations | LLM + RAG |
| 8 | **Executive Summary** | All data | Producer-friendly summary | LLM |

## 🔌 API Endpoints

```
POST   /api/v1/projects              # Create project
GET    /api/v1/projects/{id}         # Get project

POST   /api/v1/projects/{id}/upload  # Upload script

POST   /api/v1/projects/{id}/run     # Start pipeline
GET    /api/v1/projects/{id}/status  # Monitor progress

GET    /api/v1/projects/{id}/results # Dashboard JSON

POST   /api/v1/projects/{id}/whatif  # What-If simulation

GET    /api/v1/projects/{id}/report.pdf # Download PDF
```

## 📈 Example Flow

```
1. Producer uploads "Dhoom 5" script
   ↓
2. Backend extracts 28 scenes + metadata
   ↓
3. Risk Scorer processes each scene + detects 4 risky combinations
   ↓
4. Budget Estimator calculates ₹2.1M-₹3.2M range (uncertainty included)
   ↓
5. Cross-Scene Auditor finds: "Scenes 5, 18, 12 at same location but days 2, 15, 8"
   Recommendation: Reorder to 18, 5, 12 → saves ₹150K + 1 day
   ↓
6. Mitigation Planner suggests safety checks for stunt clusters
   ↓
7. Dashboard shows scene table + risk heatmap + budget pie chart
   ↓
8. Producer tweaks: "What if we move water scene to day shoot?"
   System: "Cost drops ₹100K, Risk falls 25 points" (INSTANT!)
   ↓
9. Producer clicks Download → PDF report generated
```

## 🎯 Definition of Done

✅ Upload script → scenes in DB  
✅ Run pipeline → results JSON with:
   - Scene breakdown (with evidence + confidence scores)
   - Risk scores (with amplification explained)
   - Budget ranges (min/likely/max)
   - Cross-scene insights (location chains, fatigue, etc.)
   - Mitigation recommendations  
✅ What-if endpoint → instant deltas  
✅ PDF endpoint → professional report  
✅ Dataset validator passes  

## 🛠️ Development

### Run Tests
```bash
cd backend
pytest tests/
```

### Validate Datasets
```bash
python -m app.datasets.validator
```

### Create Migration
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 📝 Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://shootsafe:shootsafe@localhost:5432/shootsafe_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Gemini LLM
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_REQUEST_DELAY=1.2

# Features
PARAPHRASE_ENABLED=true
EXTRACT_SELF_CONSISTENCY=true

# Storage
STORAGE_PATH=./storage
UPLOAD_MAX_SIZE_MB=100

# Logging
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Test thoroughly
4. Submit PR with description

## 📚 Documentation

- `docs/API_SPEC.md` → API reference
- `docs/DATASET_GUIDE.md` → How to update datasets
- `docs/AGENT_PROMPTS.md` → All LLM prompts
- `docs/DEPLOYMENT.md` → Production setup

## 🚢 Deployment

See `docs/DEPLOYMENT.md` for:
- Docker Swarm deployment
- Kubernetes setup
- Cloud provider options (AWS, GCP, Azure)
- Scaling considerations

## 📄 License

MIT License - See LICENSE file

## 👥 Team

ShootSafe AI - Hackathon Project

---

**Questions? Issues? Star this repo!** ⭐

🏴‍☠️ Built with love for film producers everywhere!
