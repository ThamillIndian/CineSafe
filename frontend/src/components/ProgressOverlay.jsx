import React from 'react';
import '../styles/components.css';

export default function ProgressOverlay({ progress }) {
  const steps = [
    { label: 'Uploading script', min: 0, max: 10 },
    { label: 'Extracting scenes', min: 10, max: 25 },
    { label: 'Analyzing risks', min: 25, max: 40 },
    { label: 'Estimating budget', min: 40, max: 60 },
    { label: 'Finding insights', min: 60, max: 75 },
    { label: 'Optimizing locations', min: 75, max: 85 },
    { label: 'Optimizing schedule', min: 85, max: 95 },
    { label: 'Finalizing report', min: 95, max: 100 },
  ];

  const currentStep = steps.find(
    s => progress >= s.min && progress < s.max
  ) || steps[steps.length - 1];

  return (
    <div className="progress-overlay">
      <div className="progress-container">
        <div className="progress-content">
          <h2>🎬 Analyzing your script...</h2>
          
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${progress}%` }}
            >
              <span className="progress-text">{Math.round(progress)}%</span>
            </div>
          </div>

          <div className="current-step">
            <span className="spinner">⚙️</span>
            <p>{currentStep.label}</p>
          </div>

          <div className="steps-timeline">
            {steps.map((step, idx) => (
              <div 
                key={idx}
                className={`step ${progress >= step.max ? 'completed' : progress >= step.min ? 'current' : ''}`}
              >
                <div className="step-dot"></div>
                <span className="step-label">{step.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
