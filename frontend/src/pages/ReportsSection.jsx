import React, { useState } from 'react';
import '../styles/reports.css';

export default function ReportsSection({ data, runId }) {
  const [loading, setLoading] = useState(false);
  const [reportStatus, setReportStatus] = useState(null);
  const [error, setError] = useState(null);

  const generateReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/reports/${runId}/generate`, {
        method: 'POST'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate report');
      }

      const result = await response.json();
      setReportStatus({
        id: result.report_id,
        status: result.status,
        generatedAt: result.generated_at,
        fileSizeMb: result.file_size_mb,
        downloadUrl: result.download_url
      });
    } catch (err) {
      console.error('Report generation failed:', err);
      setError(err.message);
    }

    setLoading(false);
  };

  const downloadReport = () => {
    if (reportStatus?.downloadUrl) {
      window.location.href = `http://localhost:8000${reportStatus.downloadUrl}`;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="reports-section">
      <div className="reports-header">
        <div className="header-content">
          <h2>📄 Generate PDF Report</h2>
          <p>
            Create a professional PDF report with all analysis findings, budget breakdowns, risk
            assessments, and producer recommendations for stakeholder review.
          </p>
        </div>
      </div>

      <div className="reports-container">
        {/* Generation Controls */}
        <div className="generation-box">
          <div className="icon-large">📋</div>

          <div className="action-content">
            <h3>Production Analysis Report</h3>
            <p className="description">
              Includes executive summary, budget optimization details, risk assessments, and
              strategic recommendations for producers and financiers.
            </p>

            <div className="button-group">
              <button
                onClick={generateReport}
                disabled={loading || (reportStatus?.status === 'already_exists')}
                className={`btn-primary ${loading ? 'loading' : ''}`}
              >
                {loading ? (
                  <>
                    <span className="spinner">⏳</span> Generating Report...
                  </>
                ) : reportStatus?.status === 'already_exists' ? (
                  <>
                    <span>✅</span> Report Ready
                  </>
                ) : (
                  <>
                    <span>📄</span> Generate Report
                  </>
                )}
              </button>

              {reportStatus && (
                <button onClick={downloadReport} className="btn-success">
                  <span>⬇️</span> Download PDF
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Status Message */}
        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">❌</span>
            <div className="alert-content">
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {reportStatus && (
          <div className="report-status">
            <div className="status-header">
              <h3>📊 Report Status</h3>
              <span className={`badge ${reportStatus.status}`}>
                {reportStatus.status === 'already_exists' ? 'Existing' : 'Just Generated'}
              </span>
            </div>

            <div className="status-details">
              <div className="detail-row">
                <span className="label">Report ID</span>
                <span className="value">{reportStatus.id}</span>
              </div>

              <div className="detail-row">
                <span className="label">Generated At</span>
                <span className="value">{formatDate(reportStatus.generatedAt)}</span>
              </div>

              <div className="detail-row">
                <span className="label">File Size</span>
                <span className="value">{reportStatus.fileSizeMb.toFixed(2)} MB</span>
              </div>

              <div className="detail-row">
                <span className="label">Status</span>
                <span className="value">
                  <span className="badge-inline success">✅ Ready for Download</span>
                </span>
              </div>
            </div>

            <div className="status-actions">
              <button
                onClick={generateReport}
                className="btn-secondary"
                title="Generate a new report (overwrites previous)"
              >
                🔄 Regenerate Report
              </button>

              <button onClick={downloadReport} className="btn-primary">
                ⬇️ Download PDF Now
              </button>
            </div>
          </div>
        )}

        {/* Report Preview Info */}
        <div className="report-preview-info">
          <h3>📋 What's Included in the Report</h3>

          <div className="preview-items">
            <div className="preview-item">
              <span className="icon">🎬</span>
              <div>
                <strong>Executive Summary</strong>
                <p>High-level overview of production analysis and key metrics</p>
              </div>
            </div>

            <div className="preview-item">
              <span className="icon">💰</span>
              <div>
                <strong>Budget Analysis</strong>
                <p>Original budget, optimization savings, and cost breakdowns</p>
              </div>
            </div>

            <div className="preview-item">
              <span className="icon">📅</span>
              <div>
                <strong>Schedule Optimization</strong>
                <p>Shooting timeline, optimization opportunities, and crew planning</p>
              </div>
            </div>

            <div className="preview-item">
              <span className="icon">⚠️</span>
              <div>
                <strong>Risk Assessment</strong>
                <p>High-risk scenes, safety protocols, and mitigation strategies</p>
              </div>
            </div>

            <div className="preview-item">
              <span className="icon">🎯</span>
              <div>
                <strong>Producer Recommendations</strong>
                <p>Strategic insights and actionable recommendations for stakeholders</p>
              </div>
            </div>

            <div className="preview-item">
              <span className="icon">📊</span>
              <div>
                <strong>Location Intelligence</strong>
                <p>Cross-scene insights and location chain optimization opportunities</p>
              </div>
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="report-notes">
          <p>
            <strong>Note:</strong> The PDF report is ideal for sharing with producers, financiers,
            and production heads. For detailed scene-by-scene analysis, use the interactive
            dashboard.
          </p>
        </div>
      </div>
    </div>
  );
}
