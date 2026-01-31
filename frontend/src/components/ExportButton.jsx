import React from 'react';
import '../styles/components.css';

export default function ExportButton({ data }) {
  const handleExportJSON = () => {
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analysis_${new Date().getTime()}.json`;
    link.click();
  };

  return (
    <div className="export-button-group">
      <button className="export-btn" onClick={handleExportJSON}>
        📥 Export JSON
      </button>
    </div>
  );
}
