"""
Mock Orchestrator Engine
Uses datasets to generate realistic results for demo/testing
Works alongside CrewAI when available
"""
import logging
from typing import Dict, Any, List
import re
import json
from datetime import datetime
import random
import uuid

logger = logging.getLogger(__name__)


class MockOrchestratorEngine:
    """
    Mock implementation that generates realistic results using datasets
    Follows the exact same workflow as the planned CrewAI pipeline
    """
    
    def __init__(self):
        """Initialize mock orchestrator"""
        logger.info("🤖 Mock Orchestrator initialized")
    
    def run_pipeline(self, project_id: str, script_text: str) -> Dict[str, Any]:
        """
        Execute mock pipeline following the planned workflow
        
        1. Extract scenes from script
        2. Calculate risk scores
        3. Estimate budgets
        4. Generate cross-scene insights
        """
        try:
            logger.info(f"🚀 Mock Pipeline Starting: {project_id}")
            
            # STEP 1: EXTRACT SCENES
            logger.info("📝 STEP 1: Scene Extraction...")
            scenes = self._extract_scenes(script_text)
            logger.info(f"   ✅ Extracted {len(scenes)} scenes")
            
            # STEP 2: CALCULATE RISKS
            logger.info("⚠️ STEP 2: Risk Scoring...")
            scenes_with_risks = self._calculate_risks(scenes)
            logger.info(f"   ✅ Risk scores calculated")
            
            # STEP 3: ESTIMATE BUDGETS
            logger.info("💰 STEP 3: Budget Estimation...")
            scenes_with_budgets = self._estimate_budgets(scenes_with_risks)
            logger.info(f"   ✅ Budget estimates calculated")
            
            # STEP 4: CROSS-SCENE AUDIT
            logger.info("🔍 STEP 4: Cross-Scene Audit...")
            insights = self._generate_insights(scenes_with_budgets)
            logger.info(f"   ✅ Generated {len(insights)} insights")
            
            logger.info("✅ Mock Pipeline Completed!")
            
            return {
                "project_id": project_id,
                "status": "completed",
                "scenes": scenes_with_budgets,
                "insights": insights,
                "summary": self._generate_summary(scenes_with_budgets, insights)
            }
        
        except Exception as e:
            logger.error(f"❌ Mock pipeline error: {e}")
            raise
    
    def _extract_scenes(self, script_text: str) -> List[Dict[str, Any]]:
        """Extract scenes from script text"""
        scenes = []
        
        # Simple regex to find scene headings (INT./EXT., LOCATION, TIME)
        scene_pattern = r"(INT\.|EXT\.)[^\n]+[\n\r]+"
        headings = re.findall(scene_pattern, script_text)
        
        if not headings:
            # If no headings, treat whole script as one scene
            headings = ["INT. GENERIC LOCATION - DAY"]
        
        # Parse each scene
        for idx, heading in enumerate(headings[:20], 1):  # Limit to 20 scenes for demo
            # Extract location
            location_match = re.search(r"(INT\.|EXT\.)\s+([^-]+)", heading)
            location = location_match.group(2).strip() if location_match else "Unknown Location"
            
            # Extract time
            time_match = re.search(r"(DAY|NIGHT|DUSK|DAWN)", heading)
            time_of_day = time_match.group(1) if time_match else "DAY"
            
            scenes.append({
                "id": str(uuid.uuid4()),
                "scene_number": idx,
                "heading": heading.strip(),
                "location": location,
                "time_of_day": time_of_day,
                "raw_text": heading,
                "extraction": {
                    "location": {"value": location, "confidence": 0.9},
                    "time_of_day": {"value": time_of_day, "confidence": 0.95},
                    "stunt_level": {"value": self._detect_stunt_level(heading), "confidence": 0.7},
                    "talent_count": {"value": self._estimate_talent(heading), "confidence": 0.6},
                    "extras_count": {"value": random.randint(0, 50), "confidence": 0.5},
                    "water_complexity": {"value": "none", "confidence": 0.9},
                    "vehicle_types": {"value": [], "confidence": 0.8},
                    "permit_tier": {"value": 1, "confidence": 0.7},
                    "weather_dependent": {"value": False, "confidence": 0.85},
                    "crowd_size": {"value": 0, "confidence": 0.7},
                    "animals": {"value": False, "confidence": 0.9},
                    "hazards": {"value": [], "confidence": 0.8},
                }
            })
        
        return scenes
    
    def _calculate_risks(self, scenes: List[Dict]) -> List[Dict]:
        """Calculate risk scores for each scene"""
        for scene in scenes:
            # Base risk scores
            stunt_level = scene["extraction"]["stunt_level"]["value"]
            
            # Risk calculation logic
            stunt_risk = {"low": 5, "medium": 12, "high": 20, "extreme": 30}.get(stunt_level, 5)
            
            scene["risk"] = {
                "safety_score": stunt_risk,
                "logistics_score": random.randint(5, 20),
                "schedule_score": random.randint(0, 15),
                "budget_score": random.randint(5, 25),
                "compliance_score": random.randint(2, 12),
                "total_risk_score": 0,
                "amplification_factor": 1.0 + (random.random() * 0.3),
                "amplification_reason": "Multi-location complexity",
                "risk_drivers": ["stunt_level", "location_complexity"]
            }
            
            scene["risk"]["total_risk_score"] = sum([
                scene["risk"]["safety_score"],
                scene["risk"]["logistics_score"],
                scene["risk"]["schedule_score"],
                scene["risk"]["budget_score"],
                scene["risk"]["compliance_score"]
            ])
        
        return scenes
    
    def _estimate_budgets(self, scenes: List[Dict]) -> List[Dict]:
        """Estimate budgets for each scene"""
        base_cost = 50000
        
        for scene in scenes:
            # Calculate multiplier based on risks
            risk_multiplier = 1.0 + (scene["risk"]["total_risk_score"] / 150.0)
            
            likely_cost = int(base_cost * risk_multiplier)
            min_cost = int(likely_cost * 0.7)
            max_cost = int(likely_cost * 1.5)
            
            scene["budget"] = {
                "cost_min": min_cost,
                "cost_likely": likely_cost,
                "cost_max": max_cost,
                "line_items": [
                    {"department": "Production", "cost": int(likely_cost * 0.4), "multiplier": 1.0},
                    {"department": "Equipment", "cost": int(likely_cost * 0.3), "multiplier": 1.0},
                    {"department": "Safety", "cost": int(likely_cost * 0.2), "multiplier": 1.2},
                    {"department": "Permits", "cost": int(likely_cost * 0.1), "multiplier": 1.0},
                ],
                "volatility_drivers": ["weather_dependency", "permit_complexity"],
                "assumptions": ["Standard crew rates", "Local permits", "No force majeure"]
            }
        
        return scenes
    
    def _generate_insights(self, scenes: List[Dict]) -> List[Dict]:
        """Generate cross-scene insights"""
        insights = []
        
        # Detect high-risk scenes
        high_risk_scenes = [s for s in scenes if s["risk"]["total_risk_score"] > 50]
        if high_risk_scenes:
            insights.append({
                "id": str(uuid.uuid4()),
                "insight_type": "SAFETY_CLUSTER",
                "scene_ids": [s["scene_number"] for s in high_risk_scenes],
                "problem_description": f"Multiple high-risk scenes detected: {len(high_risk_scenes)} scenes with risk score > 50",
                "impact_financial": sum([s["budget"]["cost_max"] for s in high_risk_scenes]) * 0.2,
                "impact_schedule": len(high_risk_scenes) * 2.5,
                "recommendation": "Consider risk mitigation strategies, increase insurance coverage, hire specialized safety personnel",
                "suggested_reorder": None,
                "confidence": 0.85
            })
        
        # Detect expensive scenes
        expensive_scenes = sorted(scenes, key=lambda s: s["budget"]["cost_likely"], reverse=True)[:3]
        if expensive_scenes:
            insights.append({
                "id": str(uuid.uuid4()),
                "insight_type": "BUDGET_CONCENTRATION",
                "scene_ids": [s["scene_number"] for s in expensive_scenes],
                "problem_description": f"Budget concentration in {len(expensive_scenes)} scenes accounting for > 40% of budget",
                "impact_financial": sum([s["budget"]["cost_likely"] for s in expensive_scenes]),
                "impact_schedule": 0.0,
                "recommendation": "Consider splitting expensive scenes or phased production approach",
                "suggested_reorder": [s["scene_number"] for s in expensive_scenes],
                "confidence": 0.8
            })
        
        # Detect multi-location complexity
        unique_locations = len(set([s["extraction"]["location"]["value"] for s in scenes]))
        if unique_locations > 3:
            insights.append({
                "id": str(uuid.uuid4()),
                "insight_type": "LOCATION_CHAIN",
                "scene_ids": list(range(1, len(scenes) + 1)),
                "problem_description": f"{unique_locations} unique locations detected - logistical complexity and transportation overhead",
                "impact_financial": len(scenes) * 5000,
                "impact_schedule": len(scenes) * 0.5,
                "recommendation": "Optimize shooting schedule by location clustering, negotiate group rates with vendors",
                "suggested_reorder": None,
                "confidence": 0.88
            })
        
        return insights
    
    def _generate_summary(self, scenes: List[Dict], insights: List[Dict]) -> Dict[str, Any]:
        """Generate executive summary"""
        total_cost_min = sum([s["budget"]["cost_min"] for s in scenes])
        total_cost_likely = sum([s["budget"]["cost_likely"] for s in scenes])
        total_cost_max = sum([s["budget"]["cost_max"] for s in scenes])
        
        avg_safety_score = sum([s["risk"]["safety_score"] for s in scenes]) / len(scenes)
        
        return {
            "total_scenes": len(scenes),
            "total_budget": {
                "min": total_cost_min,
                "likely": total_cost_likely,
                "max": total_cost_max,
                "contingency_percent": 15
            },
            "risk_summary": {
                "average_safety": int(avg_safety_score),
                "highest_risk_scene": max([s["risk"]["total_risk_score"] for s in scenes]),
            },
            "producer_summary": f"Production requires {len(scenes)} scenes across {len(set([s['extraction']['location']['value'] for s in scenes]))} locations with estimated budget of ${total_cost_likely:,}. {len(insights)} cross-scene risks identified requiring attention.",
            "feasibility_score": 0.75,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _detect_stunt_level(self, heading: str) -> str:
        """Detect stunt level from scene heading"""
        heading_lower = heading.lower()
        if any(word in heading_lower for word in ["explosion", "crash", "fight", "extreme"]):
            return "extreme"
        elif any(word in heading_lower for word in ["stunt", "action", "chase"]):
            return "high"
        elif any(word in heading_lower for word in ["fall", "jump", "water"]):
            return "medium"
        return "low"
    
    def _estimate_talent(self, heading: str) -> int:
        """Estimate talent count from scene heading"""
        heading_lower = heading.lower()
        if "crowd" in heading_lower or "party" in heading_lower:
            return 20
        elif "meeting" in heading_lower or "office" in heading_lower:
            return 5
        elif "conversation" in heading_lower or "dialogue" in heading_lower:
            return 2
        return 1


# Global mock orchestrator instance
mock_orchestrator = MockOrchestratorEngine()
