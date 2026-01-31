"""
Results API Router - Retrieve analysis results from completed runs
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import logging
from datetime import datetime

from app.database import get_db
from app.models.database import Run, Scene, SceneExtraction, SceneRisk, SceneCost, ProjectSummary, CrossSceneInsight, RunStatus
from app.models.schemas import ProjectSummaryResponse

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_run_or_404(run_id: str, session: AsyncSession):
    """Helper to get run or raise 404"""
    result = await session.execute(
        select(Run).where(Run.id == run_id)
    )
    run = result.scalars().first()
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run {run_id} not found"
        )
    
    if run.status != RunStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Run is still {run.status.value}. Check status endpoint for progress"
        )
    
    return run


# ============== GET FULL RESULTS ==============
@router.get("/{run_id}", response_model=dict)
async def get_full_results(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get complete analysis results from a run
    
    **Args:**
    - run_id: UUID of the completed run
    
    **Returns:** Full dashboard with scenes, risks, budgets, insights
    
    **Includes:**
    - Scene extractions (with confidence scores)
    - Risk scores (5 pillars + amplification)
    - Budget estimates (min/likely/max)
    - Cross-scene insights
    - Feasibility score
    - Producer summary
    
    **Note:** Only available when run status is COMPLETED
    """
    try:
        run = await get_run_or_404(run_id, session)
        
        # Get project summary if exists
        summary_result = await session.execute(
            select(ProjectSummary).where(ProjectSummary.run_id == run_id)
        )
        project_summary = summary_result.scalars().first()
        
        if project_summary:
            # Return stored summary (most complete)
            summary_data = project_summary.summary_json
            summary_data["retrieved_at"] = datetime.utcnow().isoformat()
            return summary_data
        
        # Build summary from database (fallback)
        scenes_result = await session.execute(
            select(Scene).where(Scene.run_id == run_id)
        )
        scenes = scenes_result.scalars().all()
        
        # Build scene details
        scene_data = []
        for scene in scenes:
            # Get extraction
            extraction_result = await session.execute(
                select(SceneExtraction).where(SceneExtraction.scene_id == scene.id)
            )
            extraction = extraction_result.scalars().first()
            
            # Get risk
            risk_result = await session.execute(
                select(SceneRisk).where(SceneRisk.scene_id == scene.id)
            )
            risk = risk_result.scalars().first()
            
            # Get cost
            cost_result = await session.execute(
                select(SceneCost).where(SceneCost.scene_id == scene.id)
            )
            cost = cost_result.scalars().first()
            
            scene_detail = {
                "id": scene.id,
                "scene_number": scene.scene_number,
                "location": scene.location,
                "heading": scene.heading,
                "extraction": extraction.extraction_json if extraction else None,
                "risk": {
                    "safety_score": risk.safety_score if risk else 0,
                    "logistics_score": risk.logistics_score if risk else 0,
                    "schedule_score": risk.schedule_score if risk else 0,
                    "budget_score": risk.budget_score if risk else 0,
                    "compliance_score": risk.compliance_score if risk else 0,
                    "total_score": risk.total_risk_score if risk else 0,
                    "amplification_factor": risk.amplification_factor if risk else 1.0,
                    "risk_drivers": risk.risk_drivers if risk else []
                } if risk else None,
                "budget": {
                    "cost_min": cost.cost_min if cost else 0,
                    "cost_likely": cost.cost_likely if cost else 0,
                    "cost_max": cost.cost_max if cost else 0,
                    "line_items": cost.line_items if cost else [],
                    "volatility_drivers": cost.volatility_drivers if cost else []
                } if cost else None
            }
            scene_data.append(scene_detail)
        
        # Get cross-scene insights
        insights_result = await session.execute(
            select(CrossSceneInsight).where(CrossSceneInsight.run_id == run_id)
        )
        insights = insights_result.scalars().all()
        
        insight_data = [
            {
                "id": insight.id,
                "insight_type": insight.insight_type.value,
                "scene_ids": insight.scene_ids,
                "problem_description": insight.problem_description,
                "recommendation": insight.recommendation,
                "confidence": insight.confidence
            }
            for insight in insights
        ]
        
        # Calculate aggregates
        total_budget_min = sum([s.get("budget", {}).get("cost_min", 0) for s in scene_data])
        total_budget_likely = sum([s.get("budget", {}).get("cost_likely", 0) for s in scene_data])
        total_budget_max = sum([s.get("budget", {}).get("cost_max", 0) for s in scene_data])
        
        avg_safety = sum([s.get("risk", {}).get("safety_score", 0) for s in scene_data]) / len(scene_data) if scene_data else 0
        
        return {
            "run_id": run_id,
            "project_id": run.project_id,
            "total_scenes": len(scene_data),
            "total_budget": {
                "min": total_budget_min,
                "likely": total_budget_likely,
                "max": total_budget_max
            },
            "risk_summary": {
                "average_safety": int(avg_safety),
                "highest_risk_scene": max([s["scene_number"] for s in scene_data]) if scene_data else None
            },
            "scenes": scene_data,
            "cross_scene_insights": insight_data,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching results: {str(e)}"
        )


# ============== GET SCENES ==============
@router.get("/{run_id}/scenes", response_model=list[dict])
async def get_scenes(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get all scenes from a run
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** List of all scene extractions
    """
    try:
        run = await get_run_or_404(run_id, session)
        
        scenes_result = await session.execute(
            select(Scene).where(Scene.run_id == run_id)
        )
        scenes = scenes_result.scalars().all()
        
        scene_data = []
        for scene in scenes:
            extraction_result = await session.execute(
                select(SceneExtraction).where(SceneExtraction.scene_id == scene.id)
            )
            extraction = extraction_result.scalars().first()
            
            scene_data.append({
                "id": scene.id,
                "scene_number": scene.scene_number,
                "location": scene.location,
                "heading": scene.heading,
                "extraction": extraction.extraction_json if extraction else None,
                "confidence": extraction.confidence_avg if extraction else None
            })
        
        return scene_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching scenes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching scenes: {str(e)}"
        )


# ============== GET RISK BREAKDOWN ==============
@router.get("/{run_id}/risks", response_model=list[dict])
async def get_risks(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get risk analysis for all scenes
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** Risk scores for each scene with drivers
    """
    try:
        run = await get_run_or_404(run_id, session)
        
        scenes_result = await session.execute(
            select(Scene).where(Scene.run_id == run_id)
        )
        scenes = scenes_result.scalars().all()
        
        risk_data = []
        for scene in scenes:
            risk_result = await session.execute(
                select(SceneRisk).where(SceneRisk.scene_id == scene.id)
            )
            risk = risk_result.scalars().first()
            
            if risk:
                risk_data.append({
                    "scene_id": scene.id,
                    "scene_number": scene.scene_number,
                    "location": scene.location,
                    "safety_score": risk.safety_score,
                    "logistics_score": risk.logistics_score,
                    "schedule_score": risk.schedule_score,
                    "budget_score": risk.budget_score,
                    "compliance_score": risk.compliance_score,
                    "total_risk_score": risk.total_risk_score,
                    "amplification_factor": risk.amplification_factor,
                    "amplification_reason": risk.amplification_reason,
                    "risk_drivers": risk.risk_drivers
                })
        
        # Sort by total risk (descending)
        risk_data.sort(key=lambda x: x["total_risk_score"], reverse=True)
        
        return risk_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching risks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching risks: {str(e)}"
        )


# ============== GET BUDGET BREAKDOWN ==============
@router.get("/{run_id}/budget", response_model=dict)
async def get_budget(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get complete budget analysis
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** Aggregated budget with scene breakdown
    """
    try:
        run = await get_run_or_404(run_id, session)
        
        scenes_result = await session.execute(
            select(Scene).where(Scene.run_id == run_id)
        )
        scenes = scenes_result.scalars().all()
        
        scene_budgets = []
        total_min = 0
        total_likely = 0
        total_max = 0
        
        for scene in scenes:
            cost_result = await session.execute(
                select(SceneCost).where(SceneCost.scene_id == scene.id)
            )
            cost = cost_result.scalars().first()
            
            if cost:
                scene_budgets.append({
                    "scene_number": scene.scene_number,
                    "location": scene.location,
                    "cost_min": cost.cost_min,
                    "cost_likely": cost.cost_likely,
                    "cost_max": cost.cost_max,
                    "line_items": cost.line_items,
                    "volatility_drivers": cost.volatility_drivers
                })
                
                total_min += cost.cost_min or 0
                total_likely += cost.cost_likely or 0
                total_max += cost.cost_max or 0
        
        return {
            "total_budget": {
                "min": total_min,
                "likely": total_likely,
                "max": total_max,
                "contingency_percent": 15  # Standard 15% contingency
            },
            "scene_budgets": scene_budgets,
            "budget_range_analysis": {
                "range_size": total_max - total_min,
                "range_percent": ((total_max - total_min) / total_likely * 100) if total_likely > 0 else 0,
                "volatility_assessment": "high" if ((total_max - total_min) / total_likely * 100) > 50 else "moderate" if ((total_max - total_min) / total_likely * 100) > 25 else "low"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching budget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching budget: {str(e)}"
        )


# ============== GET INSIGHTS ==============
@router.get("/{run_id}/insights", response_model=list[dict])
async def get_insights(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get cross-scene insights and optimization recommendations
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** Project-level insights from auditor agent
    """
    try:
        run = await get_run_or_404(run_id, session)
        
        insights_result = await session.execute(
            select(CrossSceneInsight).where(CrossSceneInsight.run_id == run_id)
        )
        insights = insights_result.scalars().all()
        
        insight_data = [
            {
                "id": insight.id,
                "insight_type": insight.insight_type.value,
                "scene_ids": insight.scene_ids,
                "problem_description": insight.problem_description,
                "impact_financial": insight.impact_financial,
                "impact_schedule": insight.impact_schedule,
                "recommendation": insight.recommendation,
                "suggested_reorder": insight.suggested_reorder,
                "confidence": insight.confidence
            }
            for insight in insights
        ]
        
        # Sort by confidence (descending)
        insight_data.sort(key=lambda x: x["confidence"], reverse=True)
        
        return insight_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching insights: {str(e)}"
        )
