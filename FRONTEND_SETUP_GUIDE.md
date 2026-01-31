# 🏴‍☠️ CineSafe Complete Setup Guide

## 📋 Project Overview

CineSafe is a comprehensive **Film Production Analyzer** system with:
- Backend: Python FastAPI + Qwen3 AI + SQLite
- Frontend: React + Vite + Modern CSS
- Features: Budget optimization, risk analysis, schedule planning

---

## 🚀 QUICK START (60 seconds)

### Terminal 1: Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3: LM Studio (if using Qwen3)
- Launch LM Studio
- Load `Qwen3 VI 4B` model
- Ensure API is running on `http://localhost:1234/v1`

**Then visit:** `http://localhost:3000` 🎬

---

## 🔧 DETAILED SETUP

### Prerequisites
- Python 3.9+
- Node.js 16+
- LM Studio (optional, for Qwen3)

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment (if not done)
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure database is clean (delete old shootsafe.db if exists)
rm shootsafe.db  # or del shootsafe.db on Windows

# Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend should be running at:** `http://localhost:8000`
**Swagger UI at:** `http://localhost:8000/docs`

### Step 2: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
# VITE_API_URL=http://localhost:8000/api/v1

# Start dev server
npm run dev
```

**Frontend should be running at:** `http://localhost:3000`

### Step 3: LM Studio Setup (for Qwen3)

1. Download **LM Studio** from `lm-studio.ai`
2. Open LM Studio
3. Search for **"Qwen3 VI 4B"**
4. Download and load the model
5. Start the local server (should run on `http://localhost:1234/v1`)

---

## 📁 Project Structure

```
project/
├── backend/              # FastAPI + AI pipeline
│   ├── app/
│   │   ├── agents/      # 9-agent AI system
│   │   ├── api/v1/      # REST API endpoints
│   │   ├── models/      # Database ORM models
│   │   ├── config.py    # Configuration (Qwen3/Gemini)
│   │   ├── main.py      # App entry
│   │   └── utils/       # LLM clients, helpers
│   ├── requirements.txt  # Python dependencies
│   ├── QWEN3_QUICK_START.md
│   └── venv/            # Virtual environment
│
├── frontend/            # React + Vite UI
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # API layer
│   │   ├── styles/      # CSS files
│   │   ├── App.jsx      # Main app
│   │   └── index.js     # Entry
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
│
└── latest_output.json   # Sample analysis output
```

---

## 🎯 How to Use CineSafe

### 1. Upload Script
- Go to **Home** page
- Drag & drop or click to upload a script (PDF, DOC, DOCX, TXT)
- Click **Execute Analysis**

### 2. Watch Progress
- See real-time progress with animated overlay
- Progress bar shows current stage (extraction, risks, budget, optimization, etc.)

### 3. View Analysis Results
- **Analysis Page**: 6 tabs for different views
  - 🎬 Scenes: All extracted scenes
  - ⚠️ Risk Analysis: Risk scores & drivers
  - 💰 Budget: Cost breakdown per scene
  - 🎭 Location Opt: Location clustering savings
  - 📅 Schedule Opt: Optimized shooting days
  - 👥 Department Opt: Department cost scaling

### 4. Executive Report
- View KPI cards with key metrics
- See budget optimization summary
- Read recommendations
- Export to JSON

### 5. Scene Details
- Click "View" on any scene
- See complete risk & budget data
- Check location consolidation info

---

## 🔒 Page Access Control

**Before Analysis:**
- ✅ Home page - UNLOCKED (upload here)
- 🔒 Analysis page - LOCKED
- 🔒 Executive Report - LOCKED
- 🔒 Scene Details - LOCKED

**After Analysis Completes:**
- ✅ All pages - UNLOCKED
- You can navigate freely between pages

---

## 🌐 Backend API Endpoints

### Upload & Analyze
- `POST /api/v1/scripts/upload` - Upload script file
- `POST /api/v1/runs/{documentId}/start` - Start analysis
- `GET /api/v1/runs/{runId}/result` - Get analysis results

### Full API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI

---

## ⚙️ Configuration

### Use Qwen3 vs Gemini

**File:** `backend/app/config.py`

```python
# Set to "qwen3" for local Qwen3
# Set to "gemini" for Google Gemini API
llm_provider: str = "qwen3"
```

### Qwen3 Settings
```python
qwen3_base_url: str = "http://localhost:1234/v1"
qwen3_model: str = "qwen3"
```

### Gemini Settings
```python
gemini_api_key: str = "your-api-key"
gemini_request_delay: float = 1.5
```

---

## 📊 Output Data Layers

The analysis generates **12 data layers**:

1. **Analysis Metadata** - Method, agents used, AI success rate
2. **Executive Summary** - KPIs, budget, schedule, savings
3. **Scenes Analysis** - All extracted scenes with details
4. **Risk Intelligence** - Risk scores & mitigation for each scene
5. **Budget Intelligence** - Cost breakdown per scene
6. **Cross-Scene Intelligence** - Location insights
7. **Production Recommendations** - Actionable items
8. **Location Optimization** - Location clustering savings
9. **Stunt Optimization** - Stunt relocation opportunities
10. **Schedule Optimization** - 32-day compressed schedule
11. **Department Optimization** - Department cost scaling
12. **Executive Summary (Optimization)** - Final optimization KPIs

---

## 🐛 Troubleshooting

### Issue: Backend won't start
**Error:** `Address already in use`
```bash
# Change port
python -m uvicorn app.main:app --port 8001
```

**Error:** `Database error: table runs has no column`
```bash
# Delete old database and restart
rm backend/shootsafe.db
# Restart backend - it will recreate with new schema
```

### Issue: Frontend won't connect to backend
**Check:**
- Backend is running on `http://localhost:8000`
- Frontend `package.json` has correct API URL
- Browser console for CORS errors
- Try `http://localhost:8000/docs` to verify backend is alive

### Issue: Analysis not starting
**Check:**
- Backend is running
- LM Studio is running (if using Qwen3)
- Check backend logs for errors
- Try uploading a smaller script first

### Issue: LM Studio not connecting
**Error:** `Connection refused - is LM Studio running?`
- Open LM Studio app
- Load Qwen3 VI 4B model
- Start the local server
- Verify API at `http://localhost:1234/v1/chat/completions`

---

## 🚀 Development Tips

### Hot Reload
- **Backend**: Changes auto-reload (with `--reload` flag)
- **Frontend**: Changes auto-refresh in browser

### Debug Mode
```bash
# Backend debug logging
export LOGLEVEL=DEBUG
python -m uvicorn app.main:app --reload

# Frontend debug
Open browser DevTools (F12)
```

### Clear Cache
```bash
# Backend
rm backend/shootsafe.db

# Frontend
npm cache clean --force
```

---

## 📦 Build for Production

### Backend
```bash
# Build Docker image (optional)
docker build -t cinesafe-backend .

# Or run directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm run build

# Output is in dist/ folder
# Deploy dist/ to hosting service
```

---

## 📞 Quick Reference

| Component | Port | URL |
|-----------|------|-----|
| Backend | 8000 | `http://localhost:8000` |
| Frontend | 3000 | `http://localhost:3000` |
| Backend Docs | 8000 | `http://localhost:8000/docs` |
| Swagger UI | 8000 | `http://localhost:8000/swagger` |
| LM Studio API | 1234 | `http://localhost:1234/v1` |

---

## ✅ Pre-Launch Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] Backend running on 8000
- [ ] Frontend running on 3000
- [ ] LM Studio running (if using Qwen3)
- [ ] Database file deleted (shootsafe.db)
- [ ] Can access `http://localhost:3000`
- [ ] Can see Swagger UI at `http://localhost:8000/docs`

---

## 🎬 You're Ready!

**Everything is set up and ready to analyze films like a pirate! 🏴‍☠️**

1. Open `http://localhost:3000`
2. Upload a script
3. Watch the magic happen
4. Get budget optimization insights!

---

**Happy analyzing, captain!** ⚓
