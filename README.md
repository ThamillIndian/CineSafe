# 🎬 CineSafe AI - Film Production Safety & Budgeting System

An intelligent, multi-agent system that analyzes film scripts for production risks, budgets, and logistics using **CrewAI orchestration with MCP (Model Context Protocol) server** for standardized tool access and hierarchical agent coordination.

## 🌟 Key Features

### **End-to-End Workflow**
1. **Upload Script** → PDF/DOCX → Automatic text extraction
2. **Extract Scenes** → Parse into structured scene blocks
3. **Analyze Intelligently** → **9 specialized AI agents** extract facts + risks + budget
4. **Optimize Budget** → Location clustering, schedule optimization, department scaling
5. **Dashboard** → Scene breakdown, risk charts, budget ranges, savings analysis
6. **What-If Simulation** → Instant scenario testing with LLM reasoning
7. **Download PDF** → Professional report with executive summary

### **Multi-Agent Architecture (CrewAI + MCP)**

**CrewAI Orchestration:**
- **Hierarchical coordination** - Manager agent automatically orchestrates all agents
- **Shared memory** - Agents collaborate and share context
- **Self-correction** - Agents can retry and refine outputs (max_iter=3)
- **Intelligent collaboration** - Agents can ask each other questions

**MCP Server (Model Context Protocol):**
- **Standardized tool access** - All agents access tools through MCP protocol
- **5 core tools registered:**
  - `gemini_call` - LLM access for AI-powered analysis
  - `load_dataset` - Dataset loading from CSV files
  - `extract_json` - JSON extraction and parsing
  - `get_risk_amplifiers` - Risk calculation data
  - `validate_json_schema` - Output validation
- **Industry standard** - Based on Anthropic/OpenAI MCP specification
- **Centralized resource management** - Single source of truth for tools

## 🏗️ Architecture

```
Frontend (React)
    ↓
FastAPI Backend (Python)
    ↓
CrewAI Orchestrator (Manager Agent)
    ↓
MCP Server (Tool Registry)
    ↓
9 Specialized Agents
├─ Scene Extractor Agent
├─ Risk Scorer Agent
├─ Budget Estimator Agent
├─ Cross-Scene Auditor Agent
├─ Mitigation Planner Agent
├─ Location Clusterer Agent
├─ Stunt Location Analyzer Agent
├─ Schedule Optimizer Agent
└─ Department Scaler Agent
    ↓
SQLite Database (Results Storage)
```

## 📁 Project Structure

```
scripts/                    # Optional manual tests (e.g. full pipeline dry run)
backend/
├── app/
│   ├── api/v1/              # FastAPI endpoints
│   │   ├── uploads.py       # Script upload
│   │   ├── runs.py          # Pipeline execution
│   │   ├── results.py        # Results retrieval
│   │   ├── whatif.py         # What-If analysis
│   │   └── reports.py        # PDF generation
│   ├── agents/              # 9 agent modules
│   │   ├── full_ai_orchestrator.py  # Main orchestrator (9 agents)
│   │   ├── crew_orchestrator.py     # CrewAI orchestrator (MCP)
│   │   ├── crew_agents.py           # CrewAI agent definitions
│   │   ├── crew_tasks.py            # CrewAI task definitions
│   │   ├── optimization_agents.py   # 4 optimization agents
│   │   └── ...
│   ├── utils/
│   │   ├── mcp_server.py    # MCP Server implementation
│   │   ├── mcp_tools.py     # MCP tool registration
│   │   └── llm_client.py    # Qwen3/Gemini clients
│   ├── models/
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   └── main.py             # FastAPI app entry
├── requirements.txt
└── docker-compose.yml

frontend/                     # React app
├── src/
│   ├── pages/
│   │   ├── Home.jsx         # Upload interface
│   │   ├── Analysis.jsx     # Scene analysis
│   │   ├── ExecutiveReport.jsx  # Executive summary
│   │   └── WhatIfAnalysis.jsx   # What-If scenarios
│   └── services/
│       └── api.js           # API client
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- SQLite (included with Python)

### Backend Setup

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Set environment variables
export LLM_PROVIDER="qwen3"  # or "gemini"
export QWEN3_BASE_URL="http://localhost:1234/v1"
export GEMINI_API_KEY="your_key_here"  # if using Gemini

# 3. Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Start development server
npm run dev
```

### Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📊 Database Schema

**Core Tables:**
- `documents` → Uploaded scripts (PDF/DOCX)
- `runs` → Pipeline executions with results
- `scenes` → Parsed scene data
- `scene_extractions` → AI extraction output with confidence scores
- `scene_risks` → 5-pillar risk scores (Safety, Logistics, Schedule, Budget, Compliance)
- `scene_costs` → Budget estimates (min/likely/max ranges)
- `cross_scene_insights` → Project-level inefficiencies
- `reports` → Generated PDF reports

## 🤖 The 9 Specialized Agents

### **Core Analysis Agents (5)**

| Agent | Purpose | Method | Output |
|-------|---------|--------|--------|
| **Scene Extractor** | Parse script into scenes | LLM (Qwen3/Gemini) + Regex fallback | Scene blocks with metadata |
| **Risk Scorer** | Multi-dimensional risk assessment | LLM for high-risk, templates for others | 5 risk scores (0-30 each) |
| **Budget Estimator** | Cost estimation per scene | LLM for complex, rate cards for standard | Cost ranges (min/likely/max) |
| **Cross-Scene Auditor** | Pattern detection across scenes | LLM + Rule-based | Location chains, fatigue clusters |
| **Mitigation Planner** | Generate recommendations | LLM + Templates | Actionable safety recommendations |

### **Optimization Agents (4)**

| Agent | Purpose | Method | Output |
|-------|---------|--------|--------|
| **Location Clusterer** | Group scenes by location | Deterministic clustering | Location clusters, setup savings (max 15%) |
| **Stunt Location Analyzer** | Analyze stunt relocations | Rule-based + AI | Safer alternatives, cost savings (max 8%) |
| **Schedule Optimizer** | Optimize shooting schedule | Deterministic algorithm | Day-by-day schedule, compression (max 25%) |
| **Department Scaler** | Optimize crew sizing | Rate card calculations | Department scaling, savings (max 12%) |

**Total Budget Optimization Potential:** Up to 30% savings with realistic caps

## 🔌 API Endpoints

### Scripts
- `POST /api/v1/scripts/upload` - Upload PDF/DOCX script
- `GET /api/v1/scripts/{document_id}` - Get document details
- `DELETE /api/v1/scripts/{document_id}` - Delete document

### Runs (Pipeline Execution)
- `POST /api/v1/runs/{document_id}/start` - Start analysis pipeline
- `GET /api/v1/runs/{run_id}/status` - Get execution status
- `GET /api/v1/runs/document/{document_id}` - Get run by document

### Results
- `GET /api/v1/results/{run_id}` - Get complete analysis results
- `GET /api/v1/results/{run_id}/scenes` - Get scene breakdown
- `GET /api/v1/results/{run_id}/risks` - Get risk analysis
- `GET /api/v1/results/{run_id}/budget` - Get budget analysis
- `GET /api/v1/results/{run_id}/insights` - Get cross-scene insights

### What-If Analysis
- `POST /api/v1/whatif/{run_id}` - Run custom scenario
- `POST /api/v1/whatif/{run_id}/presets/{preset_name}` - Run preset scenario
  - Presets: `budget_cut_20`, `accelerate_timeline`, `max_safety`
- `GET /api/v1/whatif/{run_id}/history` - Get scenario history

### Reports
- `POST /api/v1/reports/{run_id}/generate` - Generate PDF report
- `GET /api/v1/reports/{run_id}/download` - Download PDF report
- `GET /api/v1/reports` - List all reports

## 📈 Complete Pipeline Flow

```
1. User uploads script (PDF/DOCX)
   ↓
2. Backend extracts text, creates Document record
   ↓
3. User starts analysis → Creates Run record
   ↓
4. FullAIEnhancedOrchestrator executes 9 agents:
   
   TIER 1: Scene Extraction
   ├─ SceneExtractorAgent → Extracts scenes from script
   
   TIER 2: Analysis
   ├─ RiskScorerAgent → Calculates 5-pillar risk scores
   └─ BudgetEstimatorAgent → Estimates cost ranges
   
   TIER 3: Intelligence
   ├─ CrossSceneAuditorAgent → Finds patterns & inefficiencies
   └─ MitigationPlannerAgent → Generates recommendations
   
   TIER 4: Optimization
   ├─ LocationClustererAgent → Groups locations, saves setup costs
   ├─ StuntLocationAnalyzerAgent → Suggests safer locations
   ├─ ScheduleOptimizerAgent → Optimizes shooting schedule
   └─ DepartmentScalerAgent → Right-sizes crew departments
   ↓
5. Results stored in database:
   ├─ Run.enhanced_result_json (complete result)
   ├─ Scene records (one per scene)
   ├─ SceneExtraction (extraction data)
   ├─ SceneRisk (risk scores)
   ├─ SceneCost (budget estimates)
   └─ CrossSceneInsight (pattern insights)
   ↓
6. Frontend polls for results → Displays in Analysis page
   ↓
7. User can:
   ├─ View Executive Report (savings, recommendations)
   ├─ Run What-If scenarios (budget cuts, timeline changes)
   └─ Generate PDF report (professional documentation)
```

## 🎯 Key Technical Highlights

### **CrewAI Integration**
- **Hierarchical Process:** Manager agent automatically coordinates all agents
- **Shared Memory:** Agents share context and can reference previous work
- **Self-Correction:** Agents retry up to 3 times if output validation fails
- **Collaborative Reasoning:** Agents can ask each other questions

### **MCP Server (Model Context Protocol)**
- **Standardized Tool Access:** All agents use MCP protocol for tool calls
- **5 Registered Tools:** gemini_call, load_dataset, extract_json, get_risk_amplifiers, validate_json_schema
- **Centralized Management:** Single source of truth for all tools
- **Industry Standard:** Based on Anthropic/OpenAI MCP specification

### **Safety & Reliability**
- **AIAgentSafetyLayer:** Wraps all agent calls with error handling
- **Synthetic Data Fallbacks:** Generates default data if extraction fails
- **Realistic Caps:** Prevents unrealistic savings (location: 15%, stunt: 8%, department: 12%, schedule: 25%)
- **Eager Loading:** Prevents async database errors with SQLAlchemy

### **LLM Integration**
- **Dual LLM Support:** Qwen3 (local) or Gemini (cloud)
- **Intelligent Routing:** Uses LLM for complex scenes, templates for standard
- **Context-Aware Reasoning:** LLM receives full scene context for What-If analysis

## 📊 Datasets

5 CSV files in `backend/app/datasets/data/`:
1. **rate_card.csv** → Department costs by scale (Indie/Mid/Big Budget)
2. **city_state_multipliers.csv** → Regional cost multipliers
3. **complexity_multipliers.csv** → Scene feature → cost/risk multipliers
4. **risk_weights.csv** → Feature → risk pillar points
5. **location_library.csv** → Location type → permit tier, complexity

**Why CSV files?**
- Deterministic (no hallucination)
- Reproducible (same input = same output)
- Auditable (producer can see calculations)
- Easy to update (no code changes needed)

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

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## 📝 Environment Variables

```bash
# LLM Configuration
LLM_PROVIDER=qwen3  # or "gemini"
QWEN3_BASE_URL=http://localhost:1234/v1
QWEN3_MODEL=Qwen/Qwen2.5-VL-7B-Instruct
GEMINI_API_KEY=your_key_here  # if using Gemini

# Database
DATABASE_URL=sqlite+aiosqlite:///./shootsafe.db

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Storage
STORAGE_PATH=./storage
UPLOAD_MAX_SIZE_MB=100

# Logging
LOG_LEVEL=INFO
```

## 🎯 Definition of Done

✅ Upload script → scenes extracted and stored  
✅ Run pipeline → 9 agents execute sequentially  
✅ Results stored → Complete analysis in database  
✅ Executive summary → Budget savings, schedule compression, recommendations  
✅ What-If analysis → Scenario simulation with LLM reasoning  
✅ PDF reports → Professional documentation with all insights  
✅ CrewAI integration → Hierarchical agent coordination  
✅ MCP server → Standardized tool access for all agents  

## 🚢 Deployment

### Production Checklist
- [ ] Set `API_DEBUG=false`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up LLM API keys securely
- [ ] Configure CORS for frontend domain
- [ ] Set up file storage (S3 or similar)
- [ ] Enable logging and monitoring
- [ ] Set up backup strategy

## 📚 Documentation

- **Pipeline Flow:** See complete agent workflow above
- **API Reference:** http://localhost:8000/docs (Swagger UI)
- **Agent Architecture:** See "The 9 Specialized Agents" section
- **MCP Tools:** See `backend/app/utils/mcp_tools.py`

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Test thoroughly
4. Submit PR with description

## 📄 License

MIT License - See LICENSE file

## 👥 Team

CineSafe AI - Hackathon Project

---

**Built with CrewAI orchestration and MCP server for enterprise-grade multi-agent coordination!** 🚀

🏴‍☠️ Built with love for film producers everywhere!
