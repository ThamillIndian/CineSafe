import React from 'react';
import '../styles/components.css';

export default function DetailedSceneView({ scene, data, onClose }) {
  // Find risk data for this scene
  const riskData = data.risk_intelligence?.risks?.find(
    r => String(r.scene_number) === String(scene.scene_number)
  );

  // Find budget data for this scene
  const budgetData = data.budget_intelligence?.budgets?.find(
    b => String(b.scene_number) === String(scene.scene_number)
  );

  // Find location clusters containing this scene
  const locationClusters = data.LAYER_8_location_optimization?.location_clusters?.filter(
    cluster => cluster.scene_numbers?.includes(String(scene.scene_number))
  );

  return (
    <div className="scene-detail-modal">
      <div className="modal-overlay" onClick={onClose}></div>
      <div className="modal-content">
        <div className="modal-header">
          <h1>Scene {scene.scene_number}</h1>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Scene Info */}
          <section className="scene-info">
            <h2>📍 Scene Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <label>Location</label>
                <div className="value">{scene.location}</div>
              </div>
              <div className="info-item">
                <label>Time of Day</label>
                <div className="value">{scene.time_of_day}</div>
              </div>
              <div className="info-item">
                <label>Confidence</label>
                <div className="value">{(scene.confidence * 100).toFixed(0)}%</div>
              </div>
              <div className="info-item">
                <label>Description</label>
                <div className="value">{scene.description}</div>
              </div>
            </div>
          </section>

          {/* Risk Analysis */}
          {riskData && (
            <section className="risk-section">
              <h2>⚠️ Risk Analysis</h2>
              <div className="risk-scores">
                <div className="score">
                  <span>Total Risk</span>
                  <strong>{riskData.total_risk_score}/100</strong>
                </div>
                <div className="score">
                  <span>🛡️ Safety</span>
                  <strong>{riskData.safety_score}/100</strong>
                </div>
                <div className="score">
                  <span>🚚 Logistics</span>
                  <strong>{riskData.logistics_score}/100</strong>
                </div>
                <div className="score">
                  <span>📅 Schedule</span>
                  <strong>{riskData.schedule_score}/100</strong>
                </div>
              </div>
              <div className="risk-drivers">
                <h3>Risk Drivers:</h3>
                <ul>
                  {riskData.risk_drivers?.map((driver, i) => <li key={i}>• {driver}</li>)}
                </ul>
              </div>
              <div className="recommendations">
                <h3>Mitigation Recommendations:</h3>
                <ul>
                  {riskData.recommendations?.map((rec, i) => <li key={i}>✓ {rec}</li>)}
                </ul>
              </div>
            </section>
          )}

          {/* Budget Analysis */}
          {budgetData && (
            <section className="budget-section">
              <h2>💰 Budget Analysis</h2>
              <div className="budget-range">
                <div>Min: ₹{(budgetData.cost_min / 1000).toFixed(0)}K</div>
                <div>Likely: ₹{(budgetData.cost_likely / 1000).toFixed(0)}K</div>
                <div>Max: ₹{(budgetData.cost_max / 1000).toFixed(0)}K</div>
              </div>
              <div className="line-items">
                <h3>Department Breakdown:</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Department</th>
                      <th>Cost</th>
                      <th>Reasoning</th>
                    </tr>
                  </thead>
                  <tbody>
                    {budgetData.line_items?.map((item, i) => (
                      <tr key={i}>
                        <td>{item.department}</td>
                        <td>₹{(item.cost / 1000).toFixed(0)}K</td>
                        <td>{item.reasoning}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {/* Location Clusters */}
          {locationClusters?.length > 0 && (
            <section className="location-section">
              <h2>🎭 Location Clustering</h2>
              <div className="clusters">
                {locationClusters.map((cluster, i) => (
                  <div key={i} className="cluster">
                    <h3>{cluster.location_name}</h3>
                    <p>📍 Consolidated with <strong>{cluster.scene_count}</strong> scenes over <strong>{cluster.optimized_days}</strong> days</p>
                    <p className="efficiency">Efficiency: {cluster.efficiency_percent}%</p>
                    <p className="savings">💰 Savings: ₹{(cluster.savings / 100000).toFixed(2)}L ({((cluster.savings / cluster.setup_overhead_original) * 100).toFixed(1)}%)</p>
                    <p className="recommendation">{cluster.recommendation}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
