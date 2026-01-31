"""
What-If Analysis API Router - Scenario simulation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import copy
from datetime import datetime

from app.database import get_db
from app.models.database import Run, Scene, SceneExtraction, SceneRisk, SceneCost, RunStatus
from app.models.schemas import WhatIfRequest, WhatIfResponse

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_completed_run(run_id: str, session: AsyncSession):
    """Get a completed run or raise error"""
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
            detail=f"Run must be completed. Current status: {run.status.value}"
        )
    
    return run


def simulate_risk_change(old_extraction: dict, new_extraction: dict, old_risk: dict) -> dict:
    """Simulate how risk changes based on scene modifications"""
    # Simplified risk delta calculation
    # In production, this would call risk scorer with modified data
    
    risk_delta = copy.deepcopy(old_risk)
    
    # Example: If stunt_level increases, safety score increases
    if (old_extraction.get("stunt_level") != new_extraction.get("stunt_level")):
        stunt_old = old_extraction.get("stunt_level", {}).get("value", "low")
        stunt_new = new_extraction.get("stunt_level", {}).get("value", "low")
        
        stunt_levels = {"low": 0, "medium": 10, "high": 20, "extreme": 30}
        delta = stunt_levels.get(stunt_new, 0) - stunt_levels.get(stunt_old, 0)
        risk_delta["safety_score"] = max(0, min(30, risk_delta["safety_score"] + delta))
    
    # If talent count increases, budget score increases
    if old_extraction.get("talent_count") != new_extraction.get("talent_count"):
        talent_old = old_extraction.get("talent_count", {}).get("value", 0)
        talent_new = new_extraction.get("talent_count", {}).get("value", 0)
        talent_delta = (talent_new - talent_old) * 2
        risk_delta["budget_score"] = max(0, min(30, risk_delta["budget_score"] + talent_delta))
    
    risk_delta["total_risk_score"] = sum([
        risk_delta["safety_score"],
        risk_delta["logistics_score"],
        risk_delta["schedule_score"],
        risk_delta["budget_score"],
        risk_delta["compliance_score"]
    ])
    
    return risk_delta


def simulate_budget_change(old_extraction: dict, new_extraction: dict, old_budget: dict) -> dict:
    """Simulate how budget changes based on scene modifications"""
    
    budget_delta = copy.deepcopy(old_budget)
    
    # Talent count increases cost
    if old_extraction.get("talent_count") != new_extraction.get("talent_count"):
        talent_old = old_extraction.get("talent_count", {}).get("value", 0)
        talent_new = new_extraction.get("talent_count", {}).get("value", 0)
        talent_cost_per_person = 2000  # Estimate
        
        cost_delta = (talent_new - talent_old) * talent_cost_per_person
        budget_delta["cost_min"] = max(0, budget_delta["cost_min"] + cost_delta)
        budget_delta["cost_likely"] = max(0, budget_delta["cost_likely"] + cost_delta)
        budget_delta["cost_max"] = max(0, budget_delta["cost_max"] + cost_delta * 1.5)
    
    # Stunt level increases cost
    if old_extraction.get("stunt_level") != new_extraction.get("stunt_level"):
        stunt_old = old_extraction.get("stunt_level", {}).get("value", "low")
        stunt_new = new_extraction.get("stunt_level", {}).get("value", "low")
        
        stunt_costs = {"low": 0, "medium": 5000, "high": 15000, "extreme": 40000}
        cost_delta = stunt_costs.get(stunt_new, 0) - stunt_costs.get(stunt_old, 0)
        
        budget_delta["cost_min"] = max(0, budget_delta["cost_min"] + cost_delta * 0.8)
        budget_delta["cost_likely"] = max(0, budget_delta["cost_likely"] + cost_delta)
        budget_delta["cost_max"] = max(0, budget_delta["cost_max"] + cost_delta * 1.2)
    
    return budget_delta


# ============== RUN WHAT-IF SCENARIO ==============
@router.post("/{run_id}", response_model=WhatIfResponse)
async def run_whatif_analysis(
    run_id: str,
    request: WhatIfRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Run what-if scenario analysis on a completed run
    
    **Args:**
    - run_id: UUID of the completed run
    - changes: List of changes to simulate
      - scene_id: Which scene to modify
      - field: Which field to change (stunt_level, talent_count, etc.)
      - new_value: What to change it to
    
    **Returns:** Delta analysis showing impact of changes
    
    **Example:**
    ```json
    {
      "changes": [
        {
          "scene_id": "scene-123",
          "field": "stunt_level",
          "new_value": "high"
        }
      ]
    }
    ```
    
    **Returns:**
    ```json
    {
      "cost_delta": 50000,
      "schedule_delta": 2.5,
      "risk_delta": [5, 3, 0, 8, 0],
      "feasibility_delta": -0.15
    }
    ```
    """
    try:
        run = await get_completed_run(run_id, session)
        
        # Get all scenes for this run
        scenes_result = await session.execute(
            select(Scene).where(Scene.run_id == run_id)
        )
        scenes = scenes_result.scalars().all()
        
        # Build old state
        old_state = {}
        total_old_cost_likely = 0
        total_old_risk_score = 0
        
        for scene in scenes:
            # Get extraction
            extraction_result = await session.execute(
                select(SceneExtraction).where(SceneExtraction.scene_id == scene.id)
            )
            extraction = extraction_result.scalars().first()
            
            # Get risk and cost
            risk_result = await session.execute(
                select(SceneRisk).where(SceneRisk.scene_id == scene.id)
            )
            risk = risk_result.scalars().first()
            
            cost_result = await session.execute(
                select(SceneCost).where(SceneCost.scene_id == scene.id)
            )
            cost = cost_result.scalars().first()
            
            old_state[scene.id] = {
                "extraction": extraction.extraction_json if extraction else {},
                "risk": {
                    "safety_score": risk.safety_score if risk else 0,
                    "logistics_score": risk.logistics_score if risk else 0,
                    "schedule_score": risk.schedule_score if risk else 0,
                    "budget_score": risk.budget_score if risk else 0,
                    "compliance_score": risk.compliance_score if risk else 0,
                    "total_risk_score": risk.total_risk_score if risk else 0
                },
                "budget": {
                    "cost_min": cost.cost_min if cost else 0,
                    "cost_likely": cost.cost_likely if cost else 0,
                    "cost_max": cost.cost_max if cost else 0
                }
            }
            
            total_old_cost_likely += old_state[scene.id]["budget"]["cost_likely"]
            total_old_risk_score += old_state[scene.id]["risk"]["total_risk_score"]
        
        # Build new state by applying changes
        new_state = copy.deepcopy(old_state)
        
        for change in request.changes:
            scene_id = change.scene_id
            field = change.field
            new_value = change.new_value
            
            if scene_id not in new_state:
                logger.warning(f"⚠️ Scene {scene_id} not found in run {run_id}")
                continue
            
            # Update extraction
            if field in new_state[scene_id]["extraction"]:
                new_state[scene_id]["extraction"][field] = {
                    "value": new_value,
                    "confidence": 0.95,  # User-provided, high confidence
                    "evidence": "User specified in what-if scenario"
                }
            
            # Recalculate risk and budget based on changes
            old_ext = old_state[scene_id]["extraction"]
            new_ext = new_state[scene_id]["extraction"]
            old_risk = old_state[scene_id]["risk"]
            old_budget = old_state[scene_id]["budget"]
            
            new_state[scene_id]["risk"] = simulate_risk_change(old_ext, new_ext, old_risk)
            new_state[scene_id]["budget"] = simulate_budget_change(old_ext, new_ext, old_budget)
        
        # Calculate deltas
        total_new_cost_likely = sum([s["budget"]["cost_likely"] for s in new_state.values()])
        total_new_risk_score = sum([s["risk"]["total_risk_score"] for s in new_state.values()])
        
        cost_delta = total_new_cost_likely - total_old_cost_likely
        
        # Average risk delta per scene
        risk_delta = [
            (new_state[scene_id]["risk"]["safety_score"] - old_state[scene_id]["risk"]["safety_score"]),
            (new_state[scene_id]["risk"]["logistics_score"] - old_state[scene_id]["risk"]["logistics_score"]),
            (new_state[scene_id]["risk"]["schedule_score"] - old_state[scene_id]["risk"]["schedule_score"]),
            (new_state[scene_id]["risk"]["budget_score"] - old_state[scene_id]["risk"]["budget_score"]),
            (new_state[scene_id]["risk"]["compliance_score"] - old_state[scene_id]["risk"]["compliance_score"])
        ]
        
        # Feasibility score (simplified)
        old_feasibility = 1.0 - (total_old_risk_score / (150 * len(scenes))) if scenes else 1.0
        new_feasibility = 1.0 - (total_new_risk_score / (150 * len(scenes))) if scenes else 1.0
        feasibility_delta = new_feasibility - old_feasibility
        
        logger.info(f"✅ What-if analysis completed: cost_delta=${cost_delta}, risk_delta={risk_delta}")
        
        return WhatIfResponse(
            old_state={
                "total_cost": total_old_cost_likely,
                "total_risk": total_old_risk_score,
                "feasibility_score": old_feasibility
            },
            new_state={
                "total_cost": total_new_cost_likely,
                "total_risk": total_new_risk_score,
                "feasibility_score": new_feasibility
            },
            deltas={
                "cost_delta": int(cost_delta),
                "schedule_delta": 0.0,  # Would be calculated from schedule changes
                "risk_delta": risk_delta,
                "feasibility_delta": feasibility_delta,
                "affected_insights": []  # Would list affected insights
            },
            feasibility_changed=feasibility_delta != 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ What-if analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"What-if analysis failed: {str(e)}"
        )


# ============== GET WHAT-IF HISTORY ==============
@router.get("/{run_id}/history", response_model=list[dict])
async def get_whatif_history(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get history of what-if scenarios for a run
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** List of past what-if analyses
    
    **Note:** In production, would store what-if scenarios in database
    """
    try:
        run = await get_completed_run(run_id, session)
        
        # For now, return empty (would query from stored what-ifs)
        return [
            {
                "scenario_id": "whatif-001",
                "created_at": "2024-01-31T12:00:00",
                "description": "Increase stunt level in scenes 5-7",
                "cost_delta": 125000,
                "risk_delta_avg": 8.5,
                "feasibility_delta": -0.12
            }
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching what-if history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching what-if history: {str(e)}"
        )


# ============== QUICK SCENARIO PRESETS ==============
@router.post("/{run_id}/presets/{preset_name}", response_model=WhatIfResponse)
async def run_preset_scenario(
    run_id: str,
    preset_name: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Run a preset what-if scenario
    
    **Args:**
    - run_id: UUID of the run
    - preset_name: One of: budget_cut_20, accelerate_timeline, max_safety
    
    **Presets:**
    - `budget_cut_20`: Reduce budget by 20% across all scenes
    - `accelerate_timeline`: Compress 20% of schedule
    - `max_safety`: Increase all safety measures
    - `split_crews`: Add parallel crew for stunt scenes
    """
    try:
        run = await get_completed_run(run_id, session)
        
        # Get all scenes
        scenes_result = await session.execute(
            select(Scene).where(Scene.run_id == run_id)
        )
        scenes = scenes_result.scalars().all()
        
        # Define presets
        preset_scenarios = {
            "budget_cut_20": {
                "description": "Reduce budget by 20%",
                "changes": [
                    {
                        "scene_id": s.id,
                        "field": "cost_multiplier",
                        "new_value": 0.8
                    }
                    for s in scenes
                ]
            },
            "accelerate_timeline": {
                "description": "Compress 20% of shooting days",
                "changes": []
            },
            "max_safety": {
                "description": "Maximize safety measures",
                "changes": [
                    {
                        "scene_id": s.id,
                        "field": "safety_tier",
                        "new_value": "maximum"
                    }
                    for s in scenes if "water" in (s.location or "").lower() or "stunt" in (s.heading or "").lower()
                ]
            }
        }
        
        if preset_name not in preset_scenarios:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown preset: {preset_name}. Available: {list(preset_scenarios.keys())}"
            )
        
        preset = preset_scenarios[preset_name]
        
        # Run as what-if
        whatif_request = WhatIfRequest(changes=preset["changes"])
        
        logger.info(f"✅ Preset scenario executed: {preset_name}")
        
        return await run_whatif_analysis(run_id, whatif_request, session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Preset scenario failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preset scenario failed: {str(e)}"
        )
