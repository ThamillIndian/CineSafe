# Quick API Reference - Option B Workflow 🏴‍☠️

## 3-Step Analysis Pipeline

### STEP 1: Upload Script
```
POST /api/v1/scripts/upload
Content-Type: multipart/form-data

Body: file=@script.pdf (or .docx)

Response (202):
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "My_Film_Script.pdf",
  "format": "pdf",
  "page_count": 42,
  "uploaded_at": "2026-01-31T16:47:16.199Z"
}
```

**✅ SUCCESS:** Save `document_id` for next step

---

### STEP 2: Start Analysis
```
POST /api/v1/runs/{document_id}/start

URL: /api/v1/runs/550e8400-e29b-41d4-a716-446655440000/start

Response (202):
{
  "run_id": "660f9511-f30c-52e5-b827-557766551111",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",  # could be "running"
  "started_at": "2026-01-31T16:47:16.199Z",
  "completed_at": "2026-01-31T16:47:45.123Z"
}
```

**✅ SUCCESS:** Save `run_id` for results retrieval

---

### STEP 3: Get Results
```
GET /api/v1/results/{run_id}

URL: /api/v1/results/660f9511-f30c-52e5-b827-557766551111

Response (200):
{
  "run_id": "660f9511-f30c-52e5-b827-557766551111",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",  # Now document_id
  "status": "completed",
  "total_scenes": 20,
  "high_risk_scenes": 7,
  "total_budget": {
    "min": 943827,
    "likely": 1348327,
    "max": 2022487
  },
  "scenes": [
    {
      "id": "scene-1",
      "scene_number": 1,
      "location": "Palace Royal",
      "heading": "INT. THRONE ROOM - DAY",
      "extraction": { ... },
      "risk": {
        "safety_score": 45,
        "total_risk_score": 65,
        ...
      },
      "budget": {
        "cost_min": 50000,
        "cost_likely": 75000,
        "cost_max": 150000,
        ...
      }
    },
    ...
  ],
  "cross_scene_insights": [
    {
      "id": "insight-1",
      "insight_type": "location_chain",
      "problem_description": "Multiple high-risk scenes at same location",
      "recommendation": "Schedule together, negotiate location rates",
      ...
    }
  ],
  ...full 7-layer output...
}
```

**✅ SUCCESS:** You have full analysis results!

---

## Additional Endpoints

### Check Script Details
```
GET /api/v1/scripts/{document_id}

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "script.pdf",
  "format": "pdf",
  "page_count": 42,
  "text_length": 45231
}
```

### Check Run Status
```
GET /api/v1/runs/{run_id}/status

Response:
{
  "run_id": "660f9511-f30c-52e5-b827-557766551111",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",  # or "running", "failed"
  "started_at": "2026-01-31T16:47:16.199Z",
  "completed_at": "2026-01-31T16:47:45.123Z",
  "error": null
}
```

### List All Runs for Document
```
GET /api/v1/runs/document/{document_id}

Response:
[
  {
    "run_id": "660f9511-f30c-52e5-b827-557766551111",
    "status": "completed",
    "started_at": "2026-01-31T16:47:16.199Z",
    "completed_at": "2026-01-31T16:47:45.123Z"
  },
  ...
]
```

### Delete Script
```
DELETE /api/v1/scripts/{document_id}

Response: 204 No Content
```

---

## cURL Examples 🚀

### Upload & Analyze (One-liner for testing)
```bash
# Step 1: Upload
RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/scripts/upload" \
  -F "file=@test_script.pdf")
DOCUMENT_ID=$(echo $RESPONSE | jq -r '.document_id')
echo "Document ID: $DOCUMENT_ID"

# Step 2: Start Analysis
RUN_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/runs/$DOCUMENT_ID/start")
RUN_ID=$(echo $RUN_RESPONSE | jq -r '.run_id')
echo "Run ID: $RUN_ID"

# Step 3: Get Results
curl -s -X GET "http://127.0.0.1:8000/api/v1/results/$RUN_ID" | jq '.'
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET) |
| 201 | Created (POST with creation) |
| 202 | Accepted (async processing) |
| 204 | No Content (DELETE success) |
| 400 | Bad Request (invalid format, missing file) |
| 404 | Not Found (document/run doesn't exist) |
| 413 | File Too Large (>100MB) |
| 500 | Server Error |

---

## Testing Workflow 🧪

1. **Navigate to Swagger:**
   ```
   http://127.0.0.1:8000/docs
   ```

2. **Upload Test Script:**
   - Click "Try it out" on `/api/v1/scripts/upload`
   - Select a PDF or DOCX file
   - Execute
   - Copy `document_id` from response

3. **Start Analysis:**
   - Click "Try it out" on `/api/v1/runs/{document_id}/start`
   - Paste `document_id` in URL parameter
   - Execute
   - Copy `run_id` from response

4. **Get Results:**
   - Click "Try it out" on `/api/v1/results/{run_id}`
   - Paste `run_id` in URL parameter
   - Execute
   - See full analysis output!

---

## Performance Expectations ⏱️

| Action | Time |
|--------|------|
| Upload 50-page PDF | ~2 seconds |
| Extract text | ~1 second |
| AI Analysis (Gemini) | ~10-30 seconds |
| Total end-to-end | ~15-35 seconds |

---

## Error Handling

### File Format Error
```json
{
  "detail": "Only PDF and DOCX files are supported"
}
```

### File Size Error
```json
{
  "detail": "File exceeds limit of 100.0MB"
}
```

### Document Not Found
```json
{
  "detail": "Document 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

### Analysis Failed
```json
{
  "detail": "Failed to start run: [error details]"
}
```

---

## Pro Tips 💡

✅ Use document_id to run multiple analyses on same script
✅ Check `/api/v1/runs/document/{document_id}` to see all runs
✅ Delete unused scripts to clean up storage
✅ Status 202 means it's still processing, wait and retry
✅ Swagger UI at `/docs` has interactive testing

Shiver me timbers! Ye be ready to sail! 🏴‍☠️
