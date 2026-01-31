const API_BASE = 'http://localhost:8000/api/v1';

export async function uploadScript(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/scripts/upload`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }
  return await response.json();
}

export async function startAnalysis(documentId) {
  const response = await fetch(`${API_BASE}/runs/${documentId}/start`, {
    method: 'POST'
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Analysis start failed');
  }
  return await response.json();
}

export async function fetchAnalysisResult(runId) {
  console.log('Fetching results for run:', runId);
  const response = await fetch(`${API_BASE}/results/${runId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Fetch result failed' }));
    throw new Error(error.detail || 'Fetch result failed');
  }
  const data = await response.json();
  console.log('✅ Results fetched successfully:', data);
  return data;
}
