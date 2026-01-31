"""
Cross-Scene Auditor Agent - Project-level intelligence
ENHANCEMENT #1: Cross-Scene Intelligence for inefficiencies, fatigue, logistics
"""
from typing import Dict, List, Any
from app.utils.llm_client import gemini_client
import json
import logging

logger = logging.getLogger(__name__)


class CrossSceneAuditorAgent:
    """
    Audits entire project for cross-scene inefficiencies
    Finds location chains, fatigue clusters, resource bottlenecks
    Uses LLM to think like an experienced line producer
    """
    
    def audit_project(self, scenes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Audit entire project for inefficiencies
        
        Args:
            scenes_data: List of all scene extractions with location, time, etc.
            
        Returns:
            List of insight dicts with recommendations
        """
        
        logger.info(f"🔍 Auditing {len(scenes_data)} scenes for cross-scene inefficiencies...")
        
        # Build compact scene summaries for the LLM
        scene_summaries = self._build_scene_summaries(scenes_data)
        
        # Call LLM to analyze
        insights = self._call_auditor_llm(scene_summaries)
        
        logger.info(f"✅ Found {len(insights)} cross-scene insights")
        
        return insights
    
    def _build_scene_summaries(self, scenes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build compact summaries for LLM input
        
        Extracts: scene number, location, time, stunt, talent, extras
        """
        summaries = []
        
        for i, scene in enumerate(scenes_data):
            extraction = scene.get("extraction", {})
            risk = scene.get("risk", {})
            
            summary = {
                "scene_number": i + 1,
                "location": self._extract_field(extraction, "location"),
                "time_of_day": self._extract_field(extraction, "time_of_day"),
                "stunt_level": self._extract_field(extraction, "stunt_level"),
                "talent_count": self._extract_field(extraction, "talent_count"),
                "extras_count": self._extract_field(extraction, "extras_count"),
                "water": self._extract_field(extraction, "water_complexity"),
                "vehicles": self._extract_field(extraction, "vehicle_types"),
                "risk_score": risk.get("final_score", 0),
                "duration_hours": scene.get("duration_hours", 4),
            }
            
            summaries.append(summary)
        
        return summaries
    
    def _extract_field(self, extraction: Dict[str, Any], field: str) -> Any:
        """Extract field value from extraction"""
        if field in extraction:
            field_data = extraction[field]
            if isinstance(field_data, dict):
                return field_data.get("value", "UNKNOWN")
            return field_data
        return "UNKNOWN"
    
    def _call_auditor_llm(self, scene_summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Call Gemini to analyze cross-scene patterns
        ENHANCEMENT #1: This is where human-like producer thinking happens
        """
        
        # Build prompt for LLM
        prompt = f"""You are a 25-year veteran line producer. Analyze the shooting schedule below and identify CROSS-SCENE inefficiencies.

SCENES:
{json.dumps(scene_summaries, indent=2)}

Find inefficiencies like:
1. LOCATION CHAIN BREAKS: Same location used on different non-consecutive days (consolidate to same day block)
2. FATIGUE CLUSTERS: Too many night shoots in a row, or too many heavy stunts close together
3. TALENT OVER-UTILIZATION: Lead actor in too many scenes too close (should be clustered)
4. RESOURCE BOTTLENECKS: Multiple heavy scenes competing for same equipment/crew
5. SCHEDULE ISSUES: Tight sequence causing problems

Output ONLY valid JSON (no markdown, no explanation):
[
  {{
    "inefficiency_type": "location_chain_broken|fatigue_cluster|talent_stress|resource_bottleneck|schedule_issue",
    "scene_ids": [5, 18],
    "current_days": [2, 8],
    "problem": "Description of the problem",
    "impact": "Financial and schedule impact",
    "suggested_reorder": [18, 5, 12],
    "confidence": 0.95
  }}
]

Be concise. Only include high-confidence inefficiencies."""

        try:
            response = gemini_client.call_model(prompt, temperature=0.2)
            insights = gemini_client.extract_json_from_response(response)
            
            if isinstance(insights, list):
                return insights
            else:
                logger.warning("LLM returned non-list response")
                return []
        
        except Exception as e:
            logger.error(f"LLM error in cross-scene audit: {e}")
            return []
    
    def _analyze_location_chains(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deterministic analysis of location chain inefficiencies
        (Fallback if LLM fails)
        """
        insights = []
        
        # Group scenes by location
        location_groups = {}
        for scene in scenes:
            location = scene.get("location", "UNKNOWN")
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(scene)
        
        # Find broken chains (same location on non-consecutive days)
        for location, location_scenes in location_groups.items():
            if len(location_scenes) > 1:
                # Sort by shoot day
                sorted_scenes = sorted(
                    location_scenes,
                    key=lambda s: s.get("shoot_day", 0)
                )
                
                # Check if days are consecutive
                days = [s.get("shoot_day", 0) for s in sorted_scenes]
                
                if len(days) > 1:
                    gaps = []
                    for i in range(len(days) - 1):
                        gap = days[i + 1] - days[i]
                        if gap > 1:
                            gaps.append((i, gap))
                    
                    if gaps:
                        scene_ids = [s.get("scene_number", 0) for s in sorted_scenes]
                        insights.append({
                            "inefficiency_type": "location_chain_broken",
                            "scene_ids": scene_ids,
                            "location": location,
                            "problem": f"Location '{location}' shot on non-consecutive days",
                            "impact": f"Could save 1-2 days travel + ~${50000 * len(gaps)}",
                            "suggested_reorder": scene_ids,  # Consolidate
                            "confidence": 0.85,
                        })
        
        return insights


# Global instance
cross_scene_auditor = CrossSceneAuditorAgent()
