import React, { useState } from 'react';
import '../styles/whatif.css';

export default function WhatIfAnalysis({ data, runId }) {
  const [changes, setChanges] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('presets');

  // Extract scenes from various possible data structures
  const getScenes = () => {
    console.log('🔍 Extracting scenes from data:', Object.keys(data || {}));
    
    // Try multiple possible data structures
    if (data?.scenes && Array.isArray(data.scenes) && data.scenes.length > 0) {
      console.log('✅ Found scenes in data.scenes');
      return data.scenes;
    }
    
    if (data?.scenes_analysis?.scenes && Array.isArray(data.scenes_analysis.scenes) && data.scenes_analysis.scenes.length > 0) {
      console.log('✅ Found scenes in data.scenes_analysis.scenes');
      return data.scenes_analysis.scenes;
    }
    
    if (data?.LAYER_1_SCENE_EXTRACTIONS && Array.isArray(data.LAYER_1_SCENE_EXTRACTIONS) && data.LAYER_1_SCENE_EXTRACTIONS.length > 0) {
      console.log('✅ Found scenes in data.LAYER_1_SCENE_EXTRACTIONS');
      return data.LAYER_1_SCENE_EXTRACTIONS;
    }

    if (data?.scene_extractions && Array.isArray(data.scene_extractions) && data.scene_extractions.length > 0) {
      console.log('✅ Found scenes in data.scene_extractions');
      return data.scene_extractions;
    }
    
    // Fallback: create dummy scenes for testing
    console.warn('⚠️ No scenes found in data, creating placeholder scenes');
    return Array.from({ length: 5 }, (_, i) => ({
      id: `scene-${i + 1}`,
      scene_number: i + 1,
      heading: `Scene ${i + 1}: Sample Scene`
    }));
  };

  // Compute reference data from analysis and executive summary
  const computeReferenceData = () => {
    const scenes = getScenes();
    const riskIntel = data?.risk_intelligence || {};
    const executive = data?.LAYER_12_executive_summary || data?.executive_summary || {};
    
    return {
      totalScenes: scenes.length,
      highRiskCount: riskIntel.high_risk_count || 0,
      originalBudget: executive.original_budget_likely || 0,
      totalSavings: executive.total_savings || 0,
      scheduleCompression: executive.schedule_savings_percent || 0,
      timeline: `${executive.schedule_original_days || 0} → ${executive.schedule_optimized_days || 0} days`
    };
  };

  // Add a new change row
  const addChange = () => {
    setChanges([...changes, { scene_id: '', field: '', new_value: '' }]);
  };

  // Remove a change row
  const removeChange = (index) => {
    setChanges(changes.filter((_, i) => i !== index));
  };

  // Update a change
  const updateChange = (index, key, value) => {
    const newChanges = [...changes];
    newChanges[index][key] = value;
    setChanges(newChanges);
  };

  // Run custom scenario
  const runScenario = async () => {
    if (changes.length === 0) {
      alert('Please add at least one change');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/whatif/${runId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ changes })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
      }

      const result = await response.json();
      setResults(result);
      setActiveTab('results');
    } catch (error) {
      console.error('What-if failed:', error);
      alert(`❌ Error: ${error.message}`);
    }
    setLoading(false);
  };

  // Run preset scenario
  const runPreset = async (presetName) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/whatif/${runId}/presets/${presetName}`,
        { method: 'POST' }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Preset failed');
      }

      const result = await response.json();
      setResults(result);
      setActiveTab('results');
    } catch (error) {
      console.error('Preset failed:', error);
      alert(`❌ Error: ${error.message}`);
    }
    setLoading(false);
  };

  const scenes = getScenes();
  const fields = ['stunt_level', 'talent_count', 'location', 'safety_tier', 'equipment_level'];
  const refData = computeReferenceData();

  return (
    <div className="whatif-page">
      <div className="whatif-header">
        <h1>🎬 What-If Analysis</h1>
        <p>Simulate production changes and see their impact on budget, schedule, and risk</p>
      </div>

      {/* Tab Navigation */}
      <div className="whatif-tabs">
        <button
          className={`tab ${activeTab === 'presets' ? 'active' : ''}`}
          onClick={() => setActiveTab('presets')}
        >
          ⚡ Quick Presets
        </button>
        <button
          className={`tab ${activeTab === 'custom' ? 'active' : ''}`}
          onClick={() => setActiveTab('custom')}
        >
          🎨 Custom Scenario
        </button>
        {results && (
          <button
            className={`tab ${activeTab === 'results' ? 'active' : ''}`}
            onClick={() => setActiveTab('results')}
          >
            📊 Results
          </button>
        )}
      </div>

      {/* REFERENCE DATA DASHBOARD */}
      <div className="reference-dashboard">
        <h3>📊 Current Production Snapshot</h3>
        <div className="ref-grid">
          <div className="ref-card">
            <span className="ref-label">Total Scenes</span>
            <span className="ref-value">{refData.totalScenes}</span>
          </div>
          <div className="ref-card warning">
            <span className="ref-label">High-Risk Scenes</span>
            <span className="ref-value">{refData.highRiskCount}</span>
          </div>
          <div className="ref-card">
            <span className="ref-label">Budget</span>
            <span className="ref-value">₹{(refData.originalBudget / 1000000).toFixed(1)}M</span>
          </div>
          <div className="ref-card success">
            <span className="ref-label">Current Savings</span>
            <span className="ref-value">₹{(refData.totalSavings / 1000000).toFixed(1)}M</span>
          </div>
          <div className="ref-card">
            <span className="ref-label">Timeline</span>
            <span className="ref-value">{refData.timeline}</span>
          </div>
          <div className="ref-card">
            <span className="ref-label">Compression</span>
            <span className="ref-value">{refData.scheduleCompression.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* PRESETS TAB */}
      {activeTab === 'presets' && (
        <div className="whatif-section presets-section">
          <div className="section-content">
            <h2>⚡ Quick Scenario Presets</h2>
            <p>One-click scenarios to instantly see impact of common production changes</p>

            <div className="presets-grid">
              <div className="preset-card">
                <div className="preset-icon">💰</div>
                <h3>Budget Cut 20%</h3>
                <p>Targets the top 1/3 most expensive scenes to achieve 20% budget reduction by reducing stunt levels</p>
                <button
                  onClick={() => runPreset('budget_cut_20')}
                  disabled={loading}
                  className="btn-preset"
                >
                  {loading ? '⏳ Running...' : 'Run Scenario'}
                </button>
              </div>

              <div className="preset-card">
                <div className="preset-icon">⚡</div>
                <h3>Accelerate Timeline</h3>
                <p>Parallelizes low-risk scenes by adding crew (20% timeline compression) without compromising safety</p>
                <button
                  onClick={() => runPreset('accelerate_timeline')}
                  disabled={loading}
                  className="btn-preset"
                >
                  {loading ? '⏳ Running...' : 'Run Scenario'}
                </button>
              </div>

              <div className="preset-card">
                <div className="preset-icon">🛡️</div>
                <h3>Maximize Safety</h3>
                <p>Reduces stunt intensity in all high-risk scenes (risk score &gt; 65) for safer production</p>
                <button
                  onClick={() => runPreset('max_safety')}
                  disabled={loading}
                  className="btn-preset"
                >
                  {loading ? '⏳ Running...' : 'Run Scenario'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CUSTOM SCENARIO TAB */}
      {activeTab === 'custom' && (
        <div className="whatif-section custom-section">
          <div className="section-content">
            <h2>🎨 Build Custom Scenario</h2>
            <p>Create specific changes and see how they affect your production</p>

            <div className="changes-list">
              {changes.length === 0 ? (
                <div className="empty-state">
                  <p>No changes added yet. Click "Add Change" to get started.</p>
                </div>
              ) : (
                changes.map((change, idx) => (
                  <div key={idx} className="change-item">
                    <div className="change-number">{idx + 1}</div>

                    <div className="change-field">
                      <label>Scene</label>
                      <select
                        value={change.scene_id}
                        onChange={(e) => updateChange(idx, 'scene_id', e.target.value)}
                        className="field-input"
                      >
                        <option value="">Select Scene</option>
                        {scenes.map((s) => (
                          <option key={s.id} value={s.id}>
                            Scene {s.scene_number}: {s.heading}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="change-field">
                      <label>Field to Change</label>
                      <select
                        value={change.field}
                        onChange={(e) => updateChange(idx, 'field', e.target.value)}
                        className="field-input"
                      >
                        <option value="">Select Field</option>
                        {fields.map((f) => (
                          <option key={f} value={f}>
                            {f.replace(/_/g, ' ').toUpperCase()}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="change-field">
                      <label>New Value</label>
                      <input
                        type="text"
                        placeholder="Enter new value"
                        value={change.new_value}
                        onChange={(e) => updateChange(idx, 'new_value', e.target.value)}
                        className="field-input"
                      />
                    </div>

                    <button
                      onClick={() => removeChange(idx)}
                      className="btn-remove"
                      title="Remove this change"
                    >
                      ✕
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="changes-actions">
              <button onClick={addChange} className="btn-secondary">
                + Add Another Change
              </button>
              <button
                onClick={runScenario}
                disabled={loading || changes.length === 0}
                className="btn-primary"
              >
                {loading ? '⏳ Analyzing...' : '🚀 Run Custom Scenario'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* RESULTS TAB */}
      {activeTab === 'results' && results && (
        <div className="whatif-section results-section">
          <div className="section-content">
            <h2>📊 Analysis Results</h2>

            <div className="comparison-grid">
              {/* Original State */}
              <div className="state-card original">
                <h3>📌 Original Production</h3>
                <div className="metric">
                  <span className="metric-label">💰 Total Budget</span>
                  <span className="metric-value">
                    ₹{(results.old_state.total_cost / 1000000).toFixed(2)}M
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">⚠️ Total Risk</span>
                  <span className="metric-value">{results.old_state.total_risk.toFixed(0)}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">🎯 Feasibility</span>
                  <span className="metric-value">
                    {(results.old_state.feasibility_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Delta (Impact) */}
              <div className="state-card delta">
                <h3>📊 Impact of Changes</h3>

                <div className={`metric ${results.deltas.cost_delta < 0 ? 'positive' : 'negative'}`}>
                  <span className="metric-label">💰 Budget Change</span>
                  <span className="metric-value">
                    {results.deltas.cost_delta < 0 ? '📉' : '📈'} ₹
                    {Math.abs(results.deltas.cost_delta / 1000000).toFixed(2)}M
                  </span>
                  <span className="metric-detail">
                    {results.deltas.cost_delta < 0 ? 'Savings' : 'Additional cost'}
                  </span>
                </div>

                <div className="metric">
                  <span className="metric-label">⚠️ Risk Change</span>
                  <span className="metric-value">
                    {results.deltas.risk_delta.reduce((a, b) => a + b, 0).toFixed(0)}
                  </span>
                  <span className="metric-detail">
                    Safety: {results.deltas.risk_delta[0]}, Schedule: {results.deltas.risk_delta[2]}
                  </span>
                </div>

                <div
                  className={`metric ${results.deltas.feasibility_delta > 0 ? 'positive' : 'negative'}`}
                >
                  <span className="metric-label">🎯 Feasibility Change</span>
                  <span className="metric-value">
                    {results.deltas.feasibility_delta > 0 ? '✅' : '⚠️'}{' '}
                    {(results.deltas.feasibility_delta * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* New State */}
              <div className="state-card revised">
                <h3>📊 Revised Production</h3>
                <div className="metric">
                  <span className="metric-label">💰 Total Budget</span>
                  <span className="metric-value">
                    ₹{(results.new_state.total_cost / 1000000).toFixed(2)}M
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">⚠️ Total Risk</span>
                  <span className="metric-value">{results.new_state.total_risk.toFixed(0)}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">🎯 Feasibility</span>
                  <span className="metric-value">
                    {(results.new_state.feasibility_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Recommendation */}
            <div className="recommendation-box">
              <h3>💡 Recommendation</h3>
              {results.deltas.feasibility_delta > 0 ? (
                <p>
                  ✅ <strong>This scenario IMPROVES feasibility</strong> by{' '}
                  {(results.deltas.feasibility_delta * 100).toFixed(1)}%. The production becomes
                  easier to execute with these changes.
                </p>
              ) : (
                <p>
                  ⚠️ <strong>This scenario REDUCES feasibility</strong> by{' '}
                  {Math.abs(results.deltas.feasibility_delta * 100).toFixed(1)}%. Consider
                  alternative approaches or trade-offs.
                </p>
              )}

              {results.deltas.cost_delta < 0 && (
                <p className="savings">
                  💰 Potential Savings: ₹{Math.abs(results.deltas.cost_delta / 1000000).toFixed(2)}M
                </p>
              )}

              {/* LLM Reasoning */}
              {results.deltas.llm_reasoning && (
                <div className="llm-reasoning">
                  <h4>🤖 AI-Generated Reasoning</h4>
                  <p>{results.deltas.llm_reasoning}</p>
                </div>
              )}
            </div>

            <div className="results-actions">
              <button onClick={() => setActiveTab('custom')} className="btn-secondary">
                ← Back to Custom Scenario
              </button>
              <button onClick={() => setActiveTab('presets')} className="btn-secondary">
                Try Another Preset
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
