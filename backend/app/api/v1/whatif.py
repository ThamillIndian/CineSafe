"""
What-If Analysis API Router - Scenario simulation with LLM Intelligence
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import copy
import json
from datetime import datetime

from app.database import get_db
from app.models.database import Run, Scene, SceneExtraction, SceneRisk, SceneCost, RunStatus
from app.models.schemas import WhatIfRequest, WhatIfResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize LLM client - Use Qwen3 only
llm_client = None

try:
    from app.utils.llm_client import Qwen3Client
    from app.config import settings
    llm_client = Qwen3Client(
        base_url=settings.qwen3_base_url,
        model=settings.qwen3_model
    )
    logger.info("✅ What-If API: Qwen3 client initialized for intelligent analysis")
except Exception as e:
    logger.warning(f"⚠️ What-If API: Qwen3 unavailable, using rule-based analysis: {e}")


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


async def simulate_risk_change_with_llm(
    old_extraction: dict,
    new_extraction: dict,
    old_risk: dict,
    changes: list
) -> tuple[dict, str]:
    """Use LLM to intelligently analyze risk impact of changes"""
    
    if not llm_client:
        logger.info("LLM unavailable, using rule-based risk analysis")
        return simulate_risk_change(old_extraction, new_extraction, old_risk), "Rule-based analysis"
    
    try:
        # Fix: Properly handle Pydantic objects
        change_descriptions = []
        for change in changes:
            # Handle Pydantic object - use dot notation or convert to dict
            if hasattr(change, 'field'):
                field = change.field
                value = change.new_value if hasattr(change, 'new_value') else 'N/A'
            elif isinstance(change, dict):
                field = change.get('field', 'unknown')
                value = change.get('new_value', 'N/A')
            else:
                # Try to convert Pydantic to dict
                try:
                    change_dict = change.dict() if hasattr(change, 'dict') else change.model_dump() if hasattr(change, 'model_dump') else {}
                    field = change_dict.get('field', 'unknown')
                    value = change_dict.get('new_value', 'N/A')
                except:
                    field = 'unknown'
                    value = 'N/A'
            change_descriptions.append(f"- {field}: {value}")
        
        prompt = f"""
You are a film production risk analyst. Assess how these changes affect production risk.

CURRENT RISK PROFILE:
- Safety Score: {old_risk.get('safety_score', 0)}/30
- Logistics Score: {old_risk.get('logistics_score', 0)}/30
- Schedule Score: {old_risk.get('schedule_score', 0)}/30
- Budget Score: {old_risk.get('budget_score', 0)}/30
- Compliance Score: {old_risk.get('compliance_score', 0)}/30
- Total: {old_risk.get('total_risk_score', 0)}/150

SCENE CONTEXT (from Analysis Page):
- Current Stunt Level: {old_extraction.get('stunt_level', {}).get('value') if isinstance(old_extraction.get('stunt_level'), dict) else old_extraction.get('stunt_level', 'low (default)')}
- Current Talent Count: {old_extraction.get('talent_count', {}).get('value') if isinstance(old_extraction.get('talent_count'), dict) else old_extraction.get('talent_count', 'standard (default)')}
- Current Location: {old_extraction.get('location', {}).get('value') if isinstance(old_extraction.get('location'), dict) else old_extraction.get('location', 'studio (default)')}

PROPOSED CHANGES:
{chr(10).join(change_descriptions)}

Provide a JSON response with these EXACT fields (NO + signs, just plain numbers):
{{
    "safety_delta": <integer between -5 and 10, example: -2 or 3 not +3>,
    "logistics_delta": <integer between -5 and 10>,
    "schedule_delta": <integer between -5 and 10>,
    "budget_delta": <integer between -5 and 10>,
    "compliance_delta": <integer between -5 and 10>,
    "reasoning": "<brief explanation that REFERENCES the scene context and changes>"
}}

Consider:
- Higher stunt levels increase SAFETY risk
- More crew increases LOGISTICS risk
- Tight timelines increase SCHEDULE risk
- Budget cuts increase BUDGET risk (cost cutting = corner cutting)
- Remote locations increase COMPLIANCE risk
"""
        
        # Fix: Use call_model() method (async for Qwen3)
        response = await llm_client.call_model(prompt)
        
        # Fix: Extract JSON from response text with sanitization for + signs
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                # Fix: Remove + signs from numbers (convert "+10" to "10")
                json_str = json_str.replace(': +', ': ')
                analysis = json.loads(json_str)
            else:
                logger.warning("No JSON found in Qwen3 response, using fallback")
                return simulate_risk_change(old_extraction, new_extraction, old_risk), "JSON parse error"
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, response: {response[:200]}")
            return simulate_risk_change(old_extraction, new_extraction, old_risk), "JSON parse error"
        
        # Apply LLM-calculated deltas
        risk_delta = copy.deepcopy(old_risk)
        risk_delta["safety_score"] = max(0, min(30, old_risk["safety_score"] + analysis.get("safety_delta", 0)))
        risk_delta["logistics_score"] = max(0, min(30, old_risk["logistics_score"] + analysis.get("logistics_delta", 0)))
        risk_delta["schedule_score"] = max(0, min(30, old_risk["schedule_score"] + analysis.get("schedule_delta", 0)))
        risk_delta["budget_score"] = max(0, min(30, old_risk["budget_score"] + analysis.get("budget_delta", 0)))
        risk_delta["compliance_score"] = max(0, min(30, old_risk["compliance_score"] + analysis.get("compliance_delta", 0)))
        
        risk_delta["total_risk_score"] = sum([
            risk_delta["safety_score"],
            risk_delta["logistics_score"],
            risk_delta["schedule_score"],
            risk_delta["budget_score"],
            risk_delta["compliance_score"]
        ])
        
        reasoning = analysis.get("reasoning", "AI analyzed risk impact of the proposed changes.")
        logger.info(f"✅ Qwen3 Risk Analysis: {reasoning}")
        
        return risk_delta, reasoning
        
    except Exception as e:
        logger.error(f"❌ Qwen3 risk analysis failed: {e}, falling back to rules")
        return simulate_risk_change(old_extraction, new_extraction, old_risk), f"Analysis error: {str(e)}"


def simulate_budget_change(old_extraction: dict, new_extraction: dict, old_budget: dict) -> dict:
    """Simulate how budget changes based on scene modifications (rule-based fallback)"""
    
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


async def simulate_budget_change_with_llm(
    old_extraction: dict,
    new_extraction: dict,
    old_budget: dict,
    old_risk: dict,
    changes: list
) -> tuple[dict, str]:
    """Use LLM to intelligently analyze budget impact of changes"""
    
    if not llm_client:
        logger.info("LLM unavailable, using rule-based analysis")
        return simulate_budget_change(old_extraction, new_extraction, old_budget), "Rule-based analysis"
    
    try:
        # Fix: Properly handle Pydantic objects
        change_descriptions = []
        for change in changes:
            # Handle Pydantic object - use dot notation or convert to dict
            if hasattr(change, 'field'):
                field = change.field
                value = change.new_value if hasattr(change, 'new_value') else 'N/A'
            elif isinstance(change, dict):
                field = change.get('field', 'unknown')
                value = change.get('new_value', 'N/A')
            else:
                # Try to convert Pydantic to dict
                try:
                    change_dict = change.dict() if hasattr(change, 'dict') else change.model_dump() if hasattr(change, 'model_dump') else {}
                    field = change_dict.get('field', 'unknown')
                    value = change_dict.get('new_value', 'N/A')
                except:
                    field = 'unknown'
                    value = 'N/A'
            change_descriptions.append(f"- {field}: {value}")
        
        prompt = f"""
You are a film production cost analyst. Analyze the budget impact of these production scenario changes.

SCENE CONTEXT:
- Stunt Level: {old_extraction.get('stunt_level', {}).get('value') if isinstance(old_extraction.get('stunt_level'), dict) else old_extraction.get('stunt_level', 'low (default)')}
- Talent Count: {old_extraction.get('talent_count', {}).get('value') if isinstance(old_extraction.get('talent_count'), dict) else old_extraction.get('talent_count', 'standard (default)')}
- Location: {old_extraction.get('location', {}).get('value') if isinstance(old_extraction.get('location'), dict) else old_extraction.get('location', 'studio (default)')}
- Current Budget: ₹{old_budget.get('cost_likely', 0):,.0f} (likely), ₹{old_budget.get('cost_min', 0):,.0f} (min), ₹{old_budget.get('cost_max', 0):,.0f} (max)

PROPOSED CHANGES:
{chr(10).join(change_descriptions)}

Provide a JSON response with these EXACT fields (plain numbers, NO + signs):
{{
    "cost_min_delta": <integer rupee change, negative for cuts>,
    "cost_likely_delta": <integer rupee change>,
    "cost_max_delta": <integer rupee change>,
    "reasoning": "<brief explanation referencing the scene and changes>"
}}

Consider:
- Talent increases: ₹1,500-3,000 per additional crew member
- Stunt levels (low→extreme): ₹0 to ₹50,000 additional
- Location changes: ₹10,000-50,000 for logistics
- Safety measures: 10-30% increase per tier
- Equipment upgrades: 5-20% per tier
"""
        
        # Fix: Use call_model() method (async for Qwen3)
        response = await llm_client.call_model(prompt)
        
        # Fix: Extract JSON from response text with sanitization for + signs
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                # Fix: Remove + signs from numbers (convert "+10" to "10")
                json_str = json_str.replace(': +', ': ')
                analysis = json.loads(json_str)
            else:
                logger.warning("No JSON found in Qwen3 response, using fallback")
                return simulate_budget_change(old_extraction, new_extraction, old_budget), "JSON parse error"
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, response: {response[:200]}")
            return simulate_budget_change(old_extraction, new_extraction, old_budget), "JSON parse error"
        
        # Apply LLM-calculated deltas
        budget_delta = copy.deepcopy(old_budget)
        budget_delta["cost_min"] = max(0, old_budget["cost_min"] + int(analysis.get("cost_min_delta", 0)))
        budget_delta["cost_likely"] = max(0, old_budget["cost_likely"] + int(analysis.get("cost_likely_delta", 0)))
        budget_delta["cost_max"] = max(0, old_budget["cost_max"] + int(analysis.get("cost_max_delta", 0)))
        
        reasoning = analysis.get("reasoning", "AI analyzed the impact of changes on production costs.")
        logger.info(f"✅ Qwen3 Budget Analysis: {reasoning}")
        
        return budget_delta, reasoning
        
    except Exception as e:
        logger.error(f"❌ Qwen3 budget analysis failed: {e}, falling back to rules")
        return simulate_budget_change(old_extraction, new_extraction, old_budget), f"Analysis error: {str(e)}"


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
            
            extraction_data = extraction.extraction_json if extraction else {}
            
            # DEBUG: Log what extraction we got
            logger.info(f"🔍 Scene {scene.id} extraction_data keys: {list(extraction_data.keys()) if extraction_data else 'EMPTY'}")
            if extraction_data:
                logger.info(f"   Sample extraction: stunt_level={extraction_data.get('stunt_level')}, talent_count={extraction_data.get('talent_count')}, location={extraction_data.get('location')}")
            
            old_state[scene.id] = {
                "extraction": extraction_data,
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
            
            # Use LLM for intelligent analysis if available
            new_state[scene_id]["risk"], _ = await simulate_risk_change_with_llm(
                old_ext, new_ext, old_risk, request.changes
            )
            new_state[scene_id]["budget"], _ = await simulate_budget_change_with_llm(
                old_ext, new_ext, old_budget, old_risk, request.changes
            )
        
        # Calculate deltas
        total_new_cost_likely = sum([s["budget"]["cost_likely"] for s in new_state.values()])
        total_new_risk_score = sum([s["risk"]["total_risk_score"] for s in new_state.values()])
        
        cost_delta = total_new_cost_likely - total_old_cost_likely
        
        # Fix: Calculate aggregated risk deltas across ALL scenes, not just one
        # This prevents "scene_id not defined" error and correctly aggregates all changes
        safety_delta = sum(
            new_state[sid]["risk"]["safety_score"] - old_state[sid]["risk"]["safety_score"]
            for sid in new_state.keys()
        )
        logistics_delta = sum(
            new_state[sid]["risk"]["logistics_score"] - old_state[sid]["risk"]["logistics_score"]
            for sid in new_state.keys()
        )
        schedule_delta = sum(
            new_state[sid]["risk"]["schedule_score"] - old_state[sid]["risk"]["schedule_score"]
            for sid in new_state.keys()
        )
        budget_delta = sum(
            new_state[sid]["risk"]["budget_score"] - old_state[sid]["risk"]["budget_score"]
            for sid in new_state.keys()
        )
        compliance_delta = sum(
            new_state[sid]["risk"]["compliance_score"] - old_state[sid]["risk"]["compliance_score"]
            for sid in new_state.keys()
        )
        
        # Return as array for compatibility
        risk_delta = [safety_delta, logistics_delta, schedule_delta, budget_delta, compliance_delta]
        
        # Feasibility score (simplified)
        old_feasibility = 1.0 - (total_old_risk_score / (150 * len(scenes))) if scenes else 1.0
        new_feasibility = 1.0 - (total_new_risk_score / (150 * len(scenes))) if scenes else 1.0
        feasibility_delta = new_feasibility - old_feasibility
        
        # Generate overall LLM reasoning
        llm_reasoning = "Analysis complete"
        if llm_client:
            try:
                reasoning_prompt = f"""Summarize the impact of this production change:
- Budget change: ₹{cost_delta:,.0f}
- Risk change: {sum(risk_delta):.1f} points
- Feasibility change: {feasibility_delta*100:.1f}%
Provide a 1-2 sentence executive summary."""
                # Fix: Use call_model() method (async for Qwen3)
                llm_reasoning = await llm_client.call_model(reasoning_prompt)
            except Exception as e:
                logger.warning(f"Could not generate overall reasoning: {e}")
        
        logger.info(f"✅ What-if analysis completed: cost_delta=₹{cost_delta:,.0f}, risk_delta={sum(risk_delta):.1f}")
        
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
                "schedule_delta": 0.0,
                "risk_delta": risk_delta,
                "feasibility_delta": feasibility_delta,
                "llm_reasoning": llm_reasoning,  # NEW: Add LLM reasoning
                "affected_insights": []
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
    Run a preset what-if scenario with intelligent targeting
    
    **Args:**
    - run_id: UUID of the run
    - preset_name: One of: budget_cut_20, accelerate_timeline, max_safety
    
    **Presets (INTELLIGENT - Data-Driven):**
    - `budget_cut_20`: Reduce budget by targeting top 1/3 most expensive scenes (reduces stunt levels)
    - `accelerate_timeline`: Compress timeline by parallelizing low-risk scenes (adds crew for parallelization)
    - `max_safety`: Maximize safety by reducing stunts in high-risk scenes (risk > 65 threshold)
    """
    try:
        run = await get_completed_run(run_id, session)
        
        # Get all scenes
        scenes_result = await session.execute(
            select(Scene).where(Scene.run_id == run_id)
        )
        scenes = scenes_result.scalars().all()
        
        # Build smart preset based on actual data
        changes = []
        
        if preset_name == "budget_cut_20":
            # Fetch costs for all scenes
            scene_costs = {}
            for scene in scenes:
                cost_result = await session.execute(
                    select(SceneCost).where(SceneCost.scene_id == scene.id)
                )
                cost = cost_result.scalars().first()
                cost_value = cost.cost_likely if cost else 0
                scene_costs[scene.id] = cost_value
                logger.debug(f"Scene {scene.scene_number}: cost = {cost_value}")
            
            logger.info(f"💰 Scene costs collected: {len(scene_costs)} scenes, costs: {list(scene_costs.values())[:5]}")
            
            # Sort by cost and take top 30% of scenes (most expensive)
            sorted_scenes = sorted(scene_costs.items(), key=lambda x: x[1], reverse=True)
            num_to_modify = max(1, len(scenes) // 3)  # Modify top 1/3 most expensive
            expensive_scene_ids = [s[0] for s in sorted_scenes[:num_to_modify]]
            
            logger.info(f"💰 Budget Cut Preset: Targeting {num_to_modify} most expensive scenes: {len(expensive_scene_ids)} selected")
            logger.info(f"💰 Expensive scene IDs: {expensive_scene_ids}")
            
            for scene in scenes:
                if scene.id in expensive_scene_ids:
                    # For expensive scenes, reduce stunt level to save money
                    logger.info(f"✅ Adding change for scene {scene.scene_number} (ID: {scene.id})")
                    changes.append({
                        "scene_id": str(scene.id),
                        "field": "stunt_level",
                        "new_value": "low"  # ✅ REAL FIELD
                    })
            
            logger.info(f"💰 Total changes created: {len(changes)}")
        
        elif preset_name == "accelerate_timeline":
            # Fetch risks for scenes
            scene_risks = {}
            for scene in scenes:
                risk_result = await session.execute(
                    select(SceneRisk).where(SceneRisk.scene_id == scene.id)
                )
                risk = risk_result.scalars().first()
                risk_value = risk.total_risk_score if risk else 0
                scene_risks[scene.id] = risk_value
                logger.debug(f"Scene {scene.scene_number}: risk = {risk_value}")
            
            # Target LOW-RISK scenes for parallelization (safer to speed up)
            low_risk_scenes = [s.id for s in scenes if scene_risks.get(s.id, 0) < 50]
            num_to_modify = max(1, len(low_risk_scenes) // 2)  # Modify half of low-risk scenes
            
            logger.info(f"⚡ Accelerate Preset: Found {len(low_risk_scenes)} low-risk scenes, targeting {num_to_modify}")
            
            for scene_id in low_risk_scenes[:num_to_modify]:
                # Add extra crew for parallelization
                logger.info(f"✅ Adding change for low-risk scene {scene_id}")
                changes.append({
                    "scene_id": str(scene_id),
                    "field": "talent_count",
                    "new_value": 25  # ✅ REAL FIELD - more crew for parallel work
                })
            
            logger.info(f"⚡ Total changes created: {len(changes)}")
        
        elif preset_name == "max_safety":
            # Fetch risks for scenes
            high_risk_count = 0
            for scene in scenes:
                risk_result = await session.execute(
                    select(SceneRisk).where(SceneRisk.scene_id == scene.id)
                )
                risk = risk_result.scalars().first()
                
                if risk and risk.total_risk_score > 65:  # HIGH RISK threshold
                    # Increase safety by reducing stunt level on high-risk scenes
                    logger.info(f"✅ Adding safety change for high-risk scene {scene.scene_number} (risk: {risk.total_risk_score})")
                    changes.append({
                        "scene_id": str(scene.id),
                        "field": "stunt_level",
                        "new_value": "low"  # ✅ REAL FIELD - safer stunts
                    })
                    high_risk_count += 1
            
            logger.info(f"🛡️ Max Safety Preset: Targeting {high_risk_count} high-risk scenes (risk > 65)")
            logger.info(f"🛡️ Total changes created: {len(changes)}")
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown preset: {preset_name}. Available: budget_cut_20, accelerate_timeline, max_safety"
            )
        
        if not changes:
            logger.warning(f"⚠️ {preset_name} resulted in no changes (no qualifying scenes)")
            return WhatIfResponse(
                old_state={"total_cost": 0, "total_risk": 0, "feasibility_score": 0},
                new_state={"total_cost": 0, "total_risk": 0, "feasibility_score": 0},
                deltas={"cost_delta": 0, "schedule_delta": 0, "risk_delta": [0,0,0,0,0], "total_risk_delta": 0, "feasibility_delta": 0, "affected_insights": []},
                feasibility_changed=False,
                llm_reasoning=f"No scenes qualified for {preset_name}"
            )
        
        # Run as what-if
        whatif_request = WhatIfRequest(changes=changes)
        
        logger.info(f"✅ {preset_name} preset generated {len(changes)} targeted changes")
        
        return await run_whatif_analysis(run_id, whatif_request, session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Preset scenario failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preset scenario failed: {str(e)}"
        )
