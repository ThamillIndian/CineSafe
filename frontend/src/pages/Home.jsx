import React, { useState, useRef } from 'react';
import { uploadScript, startAnalysis } from '../services/api';
import '../styles/components.css';

export default function Home({ onAnalysisStart }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const fileInput = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleExecute = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    try {
      // Upload script
      const uploadResponse = await uploadScript(file);
      console.log('Upload response:', uploadResponse);
      const documentId = uploadResponse.document_id;
      console.log('Document ID:', documentId);

      // Start analysis
      const analysisResponse = await startAnalysis(documentId);
      console.log('Analysis response:', analysisResponse);
      const newRunId = analysisResponse.run_id;
      console.log('Run ID:', newRunId);

      // Notify parent to start progress tracking
      onAnalysisStart(newRunId);
    } catch (err) {
      console.error('Error:', err);
      setError('Error during analysis: ' + err.message);
      setUploading(false);
    }
  };

  return (
    <div className="home-page">
      <div className="home-content">
        <h1>🎬 Film Production Analyzer</h1>
        <p className="subtitle">Upload your script to analyze budget, risks, and schedule</p>

        <div 
          className={`upload-box ${dragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInput}
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleChange}
            style={{ display: 'none' }}
          />

          <div className="upload-content">
            {!file ? (
              <>
                <div className="upload-icon">📄</div>
                <h2>Drag and drop your script here</h2>
                <p>or</p>
                <button 
                  className="select-button"
                  onClick={() => fileInput.current?.click()}
                >
                  Click to select file
                </button>
                <p className="file-hint">Supported: PDF, DOC, DOCX, TXT</p>
              </>
            ) : (
              <>
                <div className="file-selected">✅</div>
                <h3>{file.name}</h3>
                <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                <button 
                  className="change-button"
                  onClick={() => fileInput.current?.click()}
                >
                  Change file
                </button>
              </>
            )}
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button 
          className="execute-button"
          onClick={handleExecute}
          disabled={!file || uploading}
        >
          {uploading ? 'Processing...' : '▶ Execute Analysis'}
        </button>
      </div>
    </div>
  );
}
