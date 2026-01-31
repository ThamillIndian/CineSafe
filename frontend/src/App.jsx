import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import ExecutiveReport from './pages/ExecutiveReport';
import DetailedSceneView from './pages/DetailedSceneView';
import ProgressOverlay from './components/ProgressOverlay';
import { useAnalysisData } from './hooks/useAnalysisData';
import { fetchAnalysisResult } from './services/api';
import './App.css';

export default function App() {
  console.log('✅ App component rendering');
  const [currentPage, setCurrentPage] = useState('home');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [selectedScene, setSelectedScene] = useState(null);
  const [runId, setRunId] = useState(null);
  
  const { data, loadData, isLoading } = useAnalysisData();
  const [isDataLoaded, setIsDataLoaded] = useState(false);

  // Check if data is available
  useEffect(() => {
    setIsDataLoaded(!!data && data.scenes_analysis && data.scenes_analysis.scenes.length > 0);
  }, [data]);

  // Lock/unlock pages based on data availability
  const canAccessPage = (page) => {
    if (page === 'home') return true; // Home always accessible
    return isDataLoaded; // Other pages only if data loaded
  };

  // Handle upload and analysis completion
  const handleAnalysisStart = async (newRunId) => {
    console.log('🎬 Analysis started with run ID:', newRunId);
    setRunId(newRunId);
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    
    // Poll for progress
    const interval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 95) return 95; // Don't reach 100 until done
        return prev + Math.random() * 20;
      });
    }, 500);

    // Poll for completion
    try {
      let completed = false;
      let attempts = 0;
      
      while (!completed && attempts < 240) { // Max 2 minutes
        try {
          console.log(`⏳ Polling attempt ${attempts + 1} for run ${newRunId}...`);
          const result = await fetchAnalysisResult(newRunId);
          
          // Successfully fetched results - run is complete!
          // Check if result has any valid data (various possible structures)
          if (result && (
            (result.scenes && result.scenes.length > 0) ||
            (result.LAYER_1_SCENE_EXTRACTIONS && result.LAYER_1_SCENE_EXTRACTIONS.length > 0) ||
            (result.total_scenes && result.total_scenes > 0) ||
            Object.keys(result).length > 0
          )) {
            console.log('✅ Results loaded successfully!', result);
            clearInterval(interval);
            await loadData(result);
            setAnalysisProgress(100);
            setIsAnalyzing(false);
            setCurrentPage('analysis');
            completed = true;
            break;
          }
        } catch (err) {
          // 404 or 202 means run not ready yet - continue polling
          console.log('⏳ Run still processing, will retry...', err.message);
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      }
      
      if (!completed) {
        console.error('❌ Analysis polling timeout');
        setIsAnalyzing(false);
        clearInterval(interval);
      }
    } catch (error) {
      console.error('❌ Analysis polling error:', error);
      clearInterval(interval);
      setIsAnalyzing(false);
    }
  };

  const handleSceneClick = (scene) => {
    setSelectedScene(scene);
    setCurrentPage('scenedetail');
  };

  const handleNavigation = (page) => {
    if (canAccessPage(page)) {
      setCurrentPage(page);
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        currentPage={currentPage} 
        onNavigate={handleNavigation}
        isDataLoaded={isDataLoaded}
      />
      
      {isAnalyzing && (
        <ProgressOverlay progress={analysisProgress} />
      )}

      <main className="main-content">
        {currentPage === 'home' && (
          <Home onAnalysisStart={handleAnalysisStart} />
        )}
        
        {currentPage === 'analysis' && isDataLoaded && (
          <Analysis 
            data={data}
            onSceneClick={handleSceneClick}
          />
        )}
        
        {currentPage === 'report' && isDataLoaded && (
          <ExecutiveReport data={data} />
        )}
        
        {currentPage === 'scenedetail' && selectedScene && (
          <DetailedSceneView 
            scene={selectedScene}
            data={data}
            onClose={() => setCurrentPage('analysis')}
          />
        )}
      </main>
    </div>
  );
}
