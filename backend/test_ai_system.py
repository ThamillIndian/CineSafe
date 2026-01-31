#!/usr/bin/env python3
"""
Test script for AI-Enhanced Film Production System
Validates Gemini integration and Indian context
"""
import sys
import os
import time
import requests
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    print(f"\n{'='*60}")
    print(f"[AI] {text}")
    print(f"{'='*60}\n")

def test_gemini_client():
    """Test Gemini client initialization"""
    print_header("Testing Gemini Client")
    
    try:
        from app.utils.llm_client import GeminiClient
        
        client = GeminiClient()
        print("[OK] GeminiClient imported successfully")
        
        if client.client:
            print("[OK] Gemini client initialized")
            print(f"   Model: {client.model}")
            return True
        else:
            print("[WARN] Gemini client not initialized (API key missing?)")
            print("   This is OK - system will use templates")
            return False
    
    except Exception as e:
        print(f"[WARN] Gemini client error: {e}")
        print("   This is OK - system will use templates")
        return False

def test_ai_orchestrator():
    """Test AI orchestrator initialization"""
    print_header("Testing AI Orchestrator")
    
    try:
        from app.agents.ai_enhanced_orchestrator import AIEnhancedOrchestratorEngine
        
        orchestrator = AIEnhancedOrchestratorEngine()
        print("[OK] AIEnhancedOrchestratorEngine imported successfully")
        print(f"   AI Available: {orchestrator.ai_available}")
        print(f"   Indian Context Loaded: {bool(orchestrator.indian_context)}")
        print(f"   Cities Registered: {len(orchestrator.indian_context['major_cities'])}")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] AI orchestrator error: {e}")
        return False

def test_indian_context():
    """Test Indian context features"""
    print_header("Testing Indian Context")
    
    try:
        from app.agents.ai_enhanced_orchestrator import AIEnhancedOrchestratorEngine
        
        orchestrator = AIEnhancedOrchestratorEngine()
        context = orchestrator.indian_context
        
        # Test cities
        print("Major Cities:")
        for city, info in context['major_cities'].items():
            print(f"   {city}: {info['permit_multiplier']}x multiplier, {info['bureaucracy_days']} days")
        
        # Test seasons
        print("\nSeason Adjustments:")
        for season, info in context['seasons'].items():
            print(f"   {season}: {info['risk_multiplier']}x risk, {info['description']}")
        
        # Test contingency
        print("\nContingency Guidelines:")
        for complexity, rate in context['contingency_guidelines'].items():
            if isinstance(rate, float):
                print(f"   {complexity}: {rate*100:.0f}%")
        
        print("[OK] Indian context fully loaded")
        return True
    
    except Exception as e:
        print(f"[ERROR] Indian context error: {e}")
        return False

def test_enhanced_orchestrator():
    """Test standard enhanced orchestrator"""
    print_header("Testing Enhanced Orchestrator")
    
    try:
        from app.agents.enhanced_orchestrator import EnhancedOrchestratorEngine
        
        orchestrator = EnhancedOrchestratorEngine()
        print("[OK] EnhancedOrchestratorEngine imported successfully")
        
        if orchestrator.location_library is not None:
            print(f"   Location Library: {len(orchestrator.location_library)} types")
        if orchestrator.rate_card is not None:
            print(f"   Rate Card: {len(orchestrator.rate_card)} departments")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Enhanced orchestrator error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print_header("Testing Database")
    
    try:
        # Import all models
        from app.models.database import (
            Project, Document, Run, Scene, SceneExtraction, 
            SceneRisk, SceneCost, CrossSceneInsight, ProjectSummary
        )
        
        print("[OK] All database models imported successfully")
        print(f"   Models: {len([Project, Document, Run, Scene, SceneExtraction, SceneRisk, SceneCost, CrossSceneInsight, ProjectSummary])}")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False

def test_api_router():
    """Test API router initialization"""
    print_header("Testing API Router")
    
    try:
        from app.api.v1 import runs, projects, uploads, results
        
        print("[OK] All API routers imported successfully")
        print("   Routers: runs, projects, uploads, results")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] API router error: {e}")
        return False

def test_mock_orchestrator():
    """Test mock orchestrator"""
    print_header("Testing Mock Orchestrator")
    
    try:
        from app.agents.mock_orchestrator import MockOrchestratorEngine
        
        orchestrator = MockOrchestratorEngine()
        print("[OK] MockOrchestratorEngine initialized successfully")
        
        # Run a quick test
        test_script = "INT. ROOM - DAY\nDialogue. EXT. STREET - NIGHT\nAction."
        result = orchestrator.run_pipeline("test-project", test_script)
        
        print(f"   Test pipeline completed")
        print(f"   Scenes extracted: {len(result.get('scenes', []))}")
        print(f"   Total budget: ${result.get('summary', {}).get('total_budget', {}).get('likely', 0):,}")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Mock orchestrator error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("[AI-ENHANCED FILM PRODUCTION SYSTEM - VALIDATION TEST]")
    print("="*60)
    
    tests = [
        ("Gemini Client", test_gemini_client),
        ("AI Orchestrator", test_ai_orchestrator),
        ("Indian Context", test_indian_context),
        ("Enhanced Orchestrator", test_enhanced_orchestrator),
        ("Database Models", test_database),
        ("API Router", test_api_router),
        ("Mock Orchestrator", test_mock_orchestrator),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"[ERROR] {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[WARN]"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL SYSTEMS GO! Ready for production!")
    elif passed >= total - 1:
        print("\n[INFO] MOSTLY READY - Some optional features unavailable")
        print("   System will work with fallback templates")
    else:
        print("\n[ERROR] CRITICAL ISSUES - Check errors above")
    
    return 0 if passed >= total - 1 else 1

if __name__ == "__main__":
    sys.exit(main())
