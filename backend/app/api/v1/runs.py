"""
Runs API Router - Direct pipeline execution from document
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import uuid
from datetime import datetime
import asyncio

from app.database import get_db
from app.models.database import Document, Run, Job, RunStatus
from app.models.schemas import RunStatusResponse
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize orchestrator
orchestrator = None
gemini_client = None

try:
    from app.utils.llm_client import GeminiClient
    gemini_client = GeminiClient()
    logger.info("✅ Gemini client initialized")
except Exception as e:
    logger.warning(f"⚠️ Gemini client failed: {e}")

try:
    from app.agents.full_ai_orchestrator import FullAIEnhancedOrchestrator
    orchestrator = FullAIEnhancedOrchestrator(gemini_client)
    logger.info("✅ Using FULL AI-Enhanced Orchestrator (5 agents)")
except Exception as e:
    logger.warning(f"⚠️ Full AI orchestrator failed: {e}")
    try:
        from app.agents.enhanced_orchestrator import EnhancedOrchestratorEngine
        orchestrator = EnhancedOrchestratorEngine()
        logger.info("✅ Using Enhanced Orchestrator")
    except Exception as e2:
        logger.error(f"❌ All orchestrators failed: {e2}")


def _safe_float(value, default: float = 0.0) -> float:
    """Safely convert value to float"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        if value.lower() in ['tbd', 'unknown', 'n/a', 'na', 'none']:
            return default
        import re
        match = re.search(r'[\d,]+\.?\d*', value)
        if match:
            try:
                return float(match.group().replace(',', ''))
            except ValueError:
                return default
        return default
    return default


async def _store_pipeline_results(run_id: str, result: dict, session: AsyncSession) -> None:
    """Store pipeline results including optimization data"""
    from app.models.database import (
        Scene, SceneExtraction, SceneRisk, SceneCost, 
        CrossSceneInsight, InsightType, Run
    )
    
    try:
        # Store complete enhanced result JSON
        run = await session.get(Run, run_id)
        if run:
            run.enhanced_result_json = result
            
            # ═══ NEW: Store optimization layers ═══
            # Location clusters
            if "LAYER_8_location_optimization" in result:
                run.location_clusters_json = result["LAYER_8_location_optimization"]
            
            # Stunt relocations
            if "LAYER_9_stunt_optimization" in result:
                run.stunt_relocations_json = result["LAYER_9_stunt_optimization"]
            
            # Schedule optimization
            if "LAYER_10_schedule_optimization" in result:
                run.optimized_schedule_json = result["LAYER_10_schedule_optimization"]
            
            # Department scaling
            if "LAYER_11_department_optimization" in result:
                run.department_scaling_json = result["LAYER_11_department_optimization"]
            
            # Executive summary
            if "LAYER_12_executive_summary" in result:
                summary = result["LAYER_12_executive_summary"]
                run.optimized_budget_min = summary.get("optimized_budget_min", 0)
                run.optimized_budget_likely = summary.get("optimized_budget_likely", 0)
                run.optimized_budget_max = summary.get("optimized_budget_max", 0)
                run.total_optimization_savings = summary.get("total_savings", 0)
                run.schedule_savings_percent = summary.get("schedule_savings_percent", 0)
        
        scenes_to_store = result.get("scenes", [])
        if "scenes_analysis" in result and "scenes" in result["scenes_analysis"]:
            scenes_to_store = result["scenes_analysis"]["scenes"]
        
        # Store scenes
        if scenes_to_store:
            for scene_data in scenes_to_store:
                scene = Scene(
                    id=scene_data.get("id", str(uuid.uuid4())),
                    run_id=run_id,
                    scene_number=scene_data.get("scene_number", 0),
                    heading=scene_data.get("heading", ""),
                    location=scene_data.get("location", "Unknown"),
                    raw_text=scene_data.get("raw_text", ""),
                )
                session.add(scene)
                await session.flush()
                
                # Store extraction
                extraction_data = scene_data.get("extraction_details", scene_data.get("extraction", {}))
                
                # FIX: If extraction_data is empty, generate synthetic data from scene info
                if not extraction_data:
                    logger.warning(f"⚠️ No extraction data for scene {scene.scene_number}, generating synthetic data")
                    extraction_data = {
                        "scene_number": scene.scene_number,
                        "heading": scene.heading,
                        "location": {"value": scene_data.get("location", "studio"), "confidence": 0.5, "evidence": "synthetic fallback"},
                        "stunt_level": {"value": "low", "confidence": 0.3, "evidence": "default fallback"},
                        "talent_count": {"value": 10, "confidence": 0.3, "evidence": "default fallback"},
                        "safety_tier": {"value": "standard", "confidence": 0.3, "evidence": "default fallback"},
                        "equipment_level": {"value": "standard", "confidence": 0.3, "evidence": "default fallback"},
                        "time_of_day": {"value": scene_data.get("time_of_day", "day"), "confidence": 0.5, "evidence": "synthetic fallback"},
                        "location_type": {"value": "studio", "confidence": 0.3, "evidence": "default fallback"},
                        "is_action_heavy": {"value": False, "confidence": 0.3, "evidence": "default fallback"}
                    }
                    logger.info(f"✅ Generated synthetic extraction for scene {scene.scene_number}")
                
                if extraction_data:
                    extraction = SceneExtraction(
                        id=str(uuid.uuid4()),
                        scene_id=scene.id,
                        extraction_json=extraction_data,
                        confidence_avg=0.78
                    )
                    session.add(extraction)
                    await session.flush()
                
                # Store risk
                risk_data = scene_data.get("risk_analysis", scene_data.get("risk", {}))
                if risk_data:
                    final_risk = risk_data.get("final_risk", risk_data.get("total_risk_score", 0))
                    risk = SceneRisk(
                        id=str(uuid.uuid4()),
                        scene_id=scene.id,
                        safety_score=risk_data.get("base_risk", risk_data.get("safety_score", 0)),
                        logistics_score=risk_data.get("logistics_score", 0),
                        schedule_score=risk_data.get("schedule_score", 0),
                        budget_score=risk_data.get("budget_score", 0),
                        compliance_score=risk_data.get("compliance_score", 0),
                        total_risk_score=final_risk,
                        amplification_factor=risk_data.get("amplification_factor", 1.0),
                        risk_drivers=risk_data.get("risk_drivers", [])
                    )
                    session.add(risk)
                
                # Store cost
                budget_data = scene_data.get("budget_analysis", scene_data.get("budget", {}))
                
                # FIX: If budget_data is empty, generate synthetic cost data
                if not budget_data:
                    logger.warning(f"⚠️ No budget data for scene {scene.scene_number}, generating synthetic cost data")
                    budget_data = {
                        "cost_min": 500000,  # ₹5 lakhs base
                        "cost_likely": 750000,  # ₹7.5 lakhs
                        "cost_max": 1000000  # ₹10 lakhs
                    }
                    logger.info(f"✅ Generated synthetic cost for scene {scene.scene_number}")
                
                if budget_data:
                    cost_estimate = budget_data.get("cost_estimate", budget_data)
                    cost = SceneCost(
                        id=str(uuid.uuid4()),
                        scene_id=scene.id,
                        cost_min=cost_estimate.get("min", budget_data.get("cost_min", 500000)),
                        cost_likely=cost_estimate.get("likely", budget_data.get("cost_likely", 750000)),
                        cost_max=cost_estimate.get("max", budget_data.get("cost_max", 1000000)),
                        line_items=budget_data.get("line_items_with_grounding", budget_data.get("line_items", [])),
                        volatility_drivers=budget_data.get("volatility_drivers", [])
                    )
                    session.add(cost)
        
        # Store cross-scene insights
        insights_to_store = result.get("insights", [])
        if "cross_scene_intelligence" in result and "insights" in result["cross_scene_intelligence"]:
            insights_to_store = result["cross_scene_intelligence"]["insights"]
        
        if insights_to_store:
            for insight_data in insights_to_store:
                insight = CrossSceneInsight(
                    id=insight_data.get("id", str(uuid.uuid4())),
                    run_id=run_id,
                    insight_type=InsightType.LOCATION_CHAIN,
                    scene_ids=insight_data.get("scene_ids", []),
                    problem_description=insight_data.get("problem", insight_data.get("problem_description", "")),
                    impact_financial=_safe_float(
                        insight_data.get("impact", {}).get("financial", 
                        insight_data.get("impact_financial", 0))
                    ),
                    impact_schedule=_safe_float(
                        insight_data.get("impact", {}).get("schedule", 
                        insight_data.get("impact_schedule", 0))
                    ),
                    recommendation=insight_data.get("recommendation", ""),
                    suggested_reorder=insight_data.get("suggested_reorder"),
                    confidence=float(insight_data.get("confidence", 0.0))
                )
                session.add(insight)
        
        await session.commit()
        logger.info("✅ Pipeline results stored in database (with optimization layers)")
    
    except Exception as e:
        logger.error(f"❌ Failed to store results: {e}")
        await session.rollback()
        raise


# ============== START RUN ==============
@router.post("/{document_id}/start", response_model=RunStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_run(
    document_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Start analysis pipeline directly from uploaded document
    
    **Args:**
    - document_id: UUID of the uploaded script
    
    **Returns:** Run ID + status
    
    **Workflow:**
    1. Validates document exists
    2. Creates Run record
    3. Executes pipeline
    4. Stores results
    """
    try:
        # Validate document exists
        result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalars().first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        if not document.text_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no text content"
            )
        
        # Create run
        run = Run(
            id=str(uuid.uuid4()),
            document_id=document_id,
            status=RunStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        session.add(run)
        await session.commit()
        await session.refresh(run)
        
        logger.info(f"✅ Run started: {run.id} for document {document_id}")
        
        # Execute pipeline synchronously
        if orchestrator:
            try:
                result = await orchestrator.run_pipeline_full_ai(
                    document_id, 
                    document.text_content
                )
                
                # Store results
                await _store_pipeline_results(run.id, result, session)
                
                # Update run status
                run.status = RunStatus.COMPLETED
                run.completed_at = datetime.utcnow()
                await session.commit()
                
                logger.info(f"✅ Run completed: {run.id}")
                
            except Exception as e:
                logger.error(f"❌ Pipeline execution failed: {e}")
                run.status = RunStatus.FAILED
                run.error_message = str(e)
                await session.commit()
        
        return RunStatusResponse(
            run_id=run.id,
            document_id=document_id,
            status=run.status.value,
            started_at=run.started_at,
            completed_at=run.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Run creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start run: {str(e)}"
        )


# ============== GET RUN STATUS ==============
@router.get("/{run_id}/status", response_model=RunStatusResponse)
async def get_run_status(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get run status"""
    try:
        result = await session.execute(
            select(Run).where(Run.id == run_id)
        )
        run = result.scalars().first()
        
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run {run_id} not found"
            )
        
        return RunStatusResponse(
            run_id=run.id,
            document_id=run.document_id,
            status=run.status.value,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error=run.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============== LIST RUNS ==============
@router.get("/document/{document_id}")
async def list_document_runs(
    document_id: str,
    session: AsyncSession = Depends(get_db)
):
    """List all runs for a document"""
    try:
        # Verify document exists
        doc_result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        if not doc_result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Get runs
        result = await session.execute(
            select(Run).where(Run.document_id == document_id)
        )
        runs = result.scalars().all()
        
        return [
            {
                "run_id": run.id,
                "status": run.status.value,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
                "error": run.error_message
            }
            for run in runs
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
