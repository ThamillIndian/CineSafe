#!/usr/bin/env python3
"""
Test Full AI Orchestrator with "Love Me If You Dare" Script
Validates all 5 agents with safe fallbacks
"""
import asyncio
import json
from pathlib import Path

async def test_full_ai_orchestrator():
    """Test the complete 5-agent pipeline"""
    
    print("\n" + "="*70)
    print("[FULL AI ORCHESTRATOR TEST]")
    print("="*70)
    
    # Load script
    script_path = Path("backend/storage/uploads/0a60b890-bba6-4dfc-931e-a56030e2bb33.pdf") or Path("Love Me If You Dare - Dubbing Script - 01.04.24 (1).pdf")
    
    if not script_path.exists():
        print(f"[ERROR] Script not found at {script_path}")
        return
    
    # Read script
    print(f"\n[STEP 1] Loading script from {script_path.name}...")
    try:
        import pdfplumber
        with pdfplumber.open(str(script_path)) as pdf:
            script_text = ""
            for page in pdf.pages:
                script_text += page.extract_text() or ""
        print(f"[OK] Script loaded: {len(script_text)} characters")
    except Exception as e:
        print(f"[ERROR] Failed to load script: {e}")
        return
    
    # Initialize orchestrator
    print("\n[STEP 2] Initializing Full AI Orchestrator...")
    try:
        from app.agents.full_ai_orchestrator import FullAIEnhancedOrchestrator
        from app.utils.llm_client import GeminiClient
        
        gemini_client = GeminiClient()
        orchestrator = FullAIEnhancedOrchestrator(gemini_client)
        print("[OK] Full AI Orchestrator initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize orchestrator: {e}")
        return
    
    # Run pipeline
    print("\n[STEP 3] Running Full AI Pipeline...")
    try:
        result = await orchestrator.run_pipeline_full_ai("test-project", script_text)
        print("[OK] Pipeline completed")
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Analyze results
    print("\n[STEP 4] Analyzing Results...")
    print(f"  - Scenes Extracted: {result['executive_summary']['total_scenes']}")
    print(f"  - High-Risk Scenes: {result['executive_summary']['high_risk_scenes']}")
    print(f"  - Total Budget (likely): ${result['executive_summary']['total_budget_likely']:,}")
    print(f"  - Cross-Scene Insights: {result['executive_summary']['cross_scene_insights']}")
    print(f"  - Recommendations: {result['executive_summary']['recommendations']}")
    
    # Check AI usage
    print("\n[STEP 5] AI Integration Report...")
    metadata = result['analysis_metadata']
    print(f"  - AI Success Rate: {metadata['ai_success_rate']:.1f}%")
    agents = metadata['agents_ai_enabled']
    agent_names = [
        "SceneExtractor",
        "RiskScorer", 
        "BudgetEstimator",
        "CrossSceneAuditor",
        "MitigationPlanner"
    ]
    for i, (name, used) in enumerate(zip(agent_names, agents)):
        status = "✓ AI" if used else "✓ Template"
        print(f"  - {name}: {status}")
    
    # Validate output structure
    print("\n[STEP 6] Validating Output Structure...")
    required_keys = [
        'run_id', 'project_id', 'status', 'analysis_metadata',
        'executive_summary', 'scenes_analysis', 'risk_intelligence',
        'budget_intelligence', 'cross_scene_intelligence',
        'production_recommendations', 'generated_at'
    ]
    missing = [k for k in required_keys if k not in result]
    if missing:
        print(f"[WARNING] Missing keys: {missing}")
    else:
        print("[OK] All required output keys present")
    
    # Validate no broken scene references
    print("\n[STEP 7] Validating Scene References...")
    scene_numbers = {s.get('scene_number') for s in result['scenes_analysis']['scenes']}
    insights = result['cross_scene_intelligence']['insights']
    broken_refs = 0
    for insight in insights:
        for scene_id in insight.get('scene_ids', []):
            if scene_id not in scene_numbers:
                broken_refs += 1
                print(f"[WARNING] Insight references non-existent scene {scene_id}")
    if broken_refs == 0:
        print("[OK] All scene references valid")
    
    # Save results
    print("\n[STEP 8] Saving Results...")
    output_path = Path("backend/test_full_ai_output.json")
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"[OK] Results saved to {output_path}")
    
    # Summary
    print("\n" + "="*70)
    print("[TEST COMPLETED]")
    print("="*70)
    print(f"✓ Scenes: {result['executive_summary']['total_scenes']}")
    print(f"✓ Risks: {result['executive_summary']['high_risk_scenes']} high-risk")
    print(f"✓ Budget: ${result['executive_summary']['total_budget_likely']:,}")
    print(f"✓ Insights: {result['executive_summary']['cross_scene_insights']}")
    print(f"✓ AI Success Rate: {metadata['ai_success_rate']:.1f}%")
    print("="*70)

if __name__ == "__main__":
    # Add backend to path
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "backend"))
    
    # Run async test
    asyncio.run(test_full_ai_orchestrator())
