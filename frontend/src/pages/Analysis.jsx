import React, { useState } from 'react';
import '../styles/components.css';

export default function Analysis({ data, onSceneClick }) {
  const [activeTab, setActiveTab] = useState('scenes');

  const tabs = [
    { id: 'scenes', label: 'Scenes', icon: '🎬' },
    { id: 'risks', label: 'Risk Analysis', icon: '⚠️' },
    { id: 'budget', label: 'Budget', icon: '💰' },
    { id: 'locations', label: 'Location Opt', icon: '🎭' },
    { id: 'schedule', label: 'Schedule Opt', icon: '📅' },
    { id: 'departments', label: 'Department Opt', icon: '👥' },
  ];

  const getRiskLevel = (sceneNumber) => {
    const risk = data.risk_intelligence?.risks?.find(
      r => String(r.scene_number) === String(sceneNumber)
    );
    if (!risk) return 'LOW';
    if (risk.total_risk_score > 80) return 'CRITICAL';
    if (risk.total_risk_score > 60) return 'HIGH';
    return 'MEDIUM';
  };

  const getRiskColor = (level) => {
    switch(level) {
      case 'CRITICAL': return '#ff6b6b';
      case 'HIGH': return '#ffa500';
      case 'MEDIUM': return '#ffd700';
      default: return '#4caf50';
    }
  };

  const getBudgetForScene = (sceneNumber) => {
    const budget = data.budget_intelligence?.budgets?.find(
      b => String(b.scene_number) === String(sceneNumber)
    );
    return budget?.cost_likely || 0;
  };

  return (
    <div className="analysis-page">
      <div className="page-header">
        <h1>📊 Analysis: {data.analysis_metadata?.analysis_type}</h1>
      </div>

      <div className="tabs-container">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="tab-content">
        {/* SCENES TAB */}
        {activeTab === 'scenes' && (
          <div className="scenes-tab">
            <h2>Scene Extraction ({data.scenes_analysis?.total_scenes} scenes)</h2>
            <div className="scenes-table">
              <table>
                <thead>
                  <tr>
                    <th>Scene #</th>
                    <th>Location</th>
                    <th>Time of Day</th>
                    <th>Risk Level</th>
                    <th>Budget</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {data.scenes_analysis?.scenes?.map((scene, idx) => {
                    const riskLevel = getRiskLevel(scene.scene_number);
                    const budget = getBudgetForScene(scene.scene_number);
                    return (
                      <tr key={idx} className="scene-row">
                        <td className="scene-number">{scene.scene_number}</td>
                        <td className="location">{scene.location}</td>
                        <td className="time-of-day">{scene.time_of_day}</td>
                        <td className="risk-level">
                          <span className="risk-badge" style={{ borderColor: getRiskColor(riskLevel) }}>
                            {riskLevel}
                          </span>
                        </td>
                        <td className="budget">₹{(budget / 1000).toFixed(0)}K</td>
                        <td>
                          <button 
                            className="detail-button"
                            onClick={() => onSceneClick(scene)}
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* RISKS TAB */}
        {activeTab === 'risks' && (
          <div className="risks-tab">
            <h2>Risk Intelligence</h2>
            <div className="risks-grid">
              {data.risk_intelligence?.risks?.map((risk, idx) => (
                <div key={idx} className="risk-card">
                  <div className="risk-header">
                    <h3>Scene {risk.scene_number}</h3>
                    <span className="risk-score">{risk.total_risk_score}/100</span>
                  </div>
                  <div className="risk-scores">
                    <div>🛡️ Safety: {risk.safety_score}</div>
                    <div>🚚 Logistics: {risk.logistics_score}</div>
                    <div>📅 Schedule: {risk.schedule_score}</div>
                    <div>💰 Budget: {risk.budget_score}</div>
                  </div>
                  <div className="risk-drivers">
                    <h4>Risk Drivers:</h4>
                    <ul>
                      {risk.risk_drivers?.slice(0, 3).map((driver, i) => (
                        <li key={i}>{driver}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* BUDGET TAB */}
        {activeTab === 'budget' && (
          <div className="budget-tab">
            <h2>Budget Intelligence</h2>
            <div className="budget-items">
              {data.budget_intelligence?.budgets?.slice(0, 20).map((budget, idx) => (
                <div key={idx} className="budget-item-card">
                  <h3>Scene {budget.scene_number}</h3>
                  <div className="budget-range">
                    <span>Min: ₹{(budget.cost_min / 1000).toFixed(0)}K</span>
                    <span>Likely: ₹{(budget.cost_likely / 1000).toFixed(0)}K</span>
                    <span>Max: ₹{(budget.cost_max / 1000).toFixed(0)}K</span>
                  </div>
                  <div className="line-items-preview">
                    {budget.line_items?.slice(0, 3).map((item, i) => (
                      <div key={i} className="line-item">
                        <span>{item.department}</span>
                        <span>₹{(item.cost / 1000).toFixed(0)}K</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* LOCATIONS OPTIMIZATION TAB */}
        {activeTab === 'locations' && (
          <div className="locations-tab">
            <h2>Location Optimization (Layer 8)</h2>
            <div className="location-clusters">
              {data.LAYER_8_location_optimization?.location_clusters?.map((cluster, idx) => (
                <div key={idx} className="location-cluster-card">
                  <h3>{cluster.location_name}</h3>
                  <div className="cluster-info">
                    <div>📍 Scenes: {cluster.scene_count}</div>
                    <div>📅 Original: {cluster.unoptimized_days} days</div>
                    <div>⚡ Optimized: {cluster.optimized_days} days</div>
                    <div className="savings">💰 Savings: ₹{(cluster.savings / 100000).toFixed(2)}L</div>
                  </div>
                  <p className="efficiency">Efficiency: {cluster.efficiency_percent}%</p>
                  <p className="recommendation">{cluster.recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SCHEDULE OPTIMIZATION TAB */}
        {activeTab === 'schedule' && (
          <div className="schedule-tab">
            <h2>Schedule Optimization (Layer 10)</h2>
            <div className="schedule-summary">
              <div className="stat">
                <span className="label">Total Days</span>
                <span className="value">{data.LAYER_10_schedule_optimization?.total_production_days}</span>
              </div>
              <div className="stat">
                <span className="label">Shooting Days</span>
                <span className="value">{data.LAYER_10_schedule_optimization?.total_shooting_days}</span>
              </div>
              <div className="stat">
                <span className="label">Time Savings</span>
                <span className="value">{data.LAYER_10_schedule_optimization?.time_savings_percent?.toFixed(1)}%</span>
              </div>
            </div>
            <div className="schedule-days">
              {data.LAYER_10_schedule_optimization?.daily_breakdown?.slice(0, 10).map((day, idx) => (
                <div key={idx} className="schedule-day-card">
                  <h4>Day {day.day}</h4>
                  <p>{day.location}</p>
                  <p className="scenes">Scenes: {day.scenes?.join(', ') || 'TBD'}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* DEPARTMENTS OPTIMIZATION TAB */}
        {activeTab === 'departments' && (
          <div className="departments-tab">
            <h2>Department Optimization (Layer 11)</h2>
            <div className="departments-table">
              <table>
                <thead>
                  <tr>
                    <th>Department</th>
                    <th>Unoptimized</th>
                    <th>Optimized</th>
                    <th>Savings</th>
                    <th>Factor</th>
                  </tr>
                </thead>
                <tbody>
                  {data.LAYER_11_department_optimization?.departments?.map((dept, idx) => (
                    <tr key={idx}>
                      <td>{dept.department}</td>
                      <td>₹{(dept.unoptimized_cost / 100000).toFixed(2)}L</td>
                      <td>₹{(dept.optimized_cost / 100000).toFixed(2)}L</td>
                      <td className="savings">₹{(dept.savings / 100000).toFixed(2)}L</td>
                      <td>{(dept.scaling_factor * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
