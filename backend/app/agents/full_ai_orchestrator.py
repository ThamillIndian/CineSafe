"""
Full AI-Enhanced Orchestrator Engine
5 Agents with AI-first strategy + Safe Fallbacks
Maximum Jury Impact + Minimum Risk
"""
import logging
import json
import uuid
import re
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
# SAFETY LAYER: Universal Error Handling
# ════════════════════════════════════════════════════════════════

class AIAgentSafetyLayer:
    """Ensures graceful degradation across all agents"""
    
    async def execute_with_safety(self, agent, method_name, *args, **kwargs):
        """Execute any agent method with full error handling"""
        agent_name = agent.__class__.__name__
        
        try:
            logger.info(f"🚀 {agent_name}: Starting {method_name}...")
            result = await getattr(agent, method_name)(*args, **kwargs)
            
            if self._validate_result(result):
                logger.info(f"✅ {agent_name}: Success")
                return result
            else:
                logger.warning(f"⚠️ {agent_name}: Invalid result, using fallback")
                return self._get_fallback_result(method_name)
        
        except TimeoutError:
            logger.warning(f"⏱️ {agent_name}: Timeout, using fallback")
            return self._get_fallback_result(method_name)
        
        except Exception as e:
            logger.error(f"❌ {agent_name}: {str(e)}, using fallback")
            return self._get_fallback_result(method_name)
    
    def _validate_result(self, result):
        """Check result quality"""
        if not result:
            return False
        if 'scenes' in result:
            return len(result.get('scenes', [])) > 0
        if 'risks' in result:
            return len(result.get('risks', [])) > 0
        if 'budgets' in result:
            return len(result.get('budgets', [])) >= 0  # Can be 0
        return True
    
    def _get_fallback_result(self, method_name):
        """Return safe default for any agent"""
        fallbacks = {
            'extract_scenes': {'scenes': [], 'ai_used': False, 'confidence': 0.5, 'agent_name': 'SceneExtractorAgent'},
            'analyze_risks': {'risks': [], 'ai_used': False, 'confidence': 0.5, 'agent_name': 'RiskScorerAgent'},
            'estimate_budget': {'budgets': [], 'ai_used': False, 'confidence': 0.5, 'agent_name': 'BudgetEstimatorAgent'},
            'find_insights': {'insights': [], 'ai_used': False, 'confidence': 0.5, 'agent_name': 'CrossSceneAuditorAgent'},
            'generate_recommendations': {'recommendations': [], 'ai_used': False, 'confidence': 0.5, 'agent_name': 'MitigationPlannerAgent'},
            'cluster_locations': {'location_clusters': [], 'total_location_savings': 0, 'clusters_found': 0, 'confidence': 0.5},
            'analyze_stunt_relocations': {'stunt_relocations': [], 'total_stunt_savings': 0, 'confidence': 0.5},
            'optimize_schedule': {'total_shooting_days': 0, 'total_setup_days': 0, 'total_production_days': 0, 'time_savings_percent': 0, 'daily_breakdown': [], 'confidence': 0.5},
            'scale_departments': {'departments': [], 'total_department_savings': 0, 'confidence': 0.5}
        }
        return fallbacks.get(method_name, {})


# ════════════════════════════════════════════════════════════════
# AGENT 1: SCENE EXTRACTOR
# ════════════════════════════════════════════════════════════════

class SceneExtractorAgent:
    """Extract scenes with AI-first, regex fallback"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def extract_scenes(self, script_text: str) -> Dict[str, Any]:
        """TRY: LLM AI on FULL SCRIPT → FALLBACK: Multi-pattern regex"""
        
        extracted_scenes = []
        ai_success = False
        
        # Log input size for debugging
        logger.info(f"📄 SceneExtractor: Processing {len(script_text):,} characters")
        logger.info(f"📄 SceneExtractor: {len(script_text.split(chr(10)))} lines in script")
        
        # ═══ PHASE 1: TRY AI WITH FULL SCRIPT ═══
        if self.llm_client and len(script_text) > 100:
            try:
                logger.info("📞 SceneExtractor: Calling LLM AI...")
                
                prompt = f"""Extract ALL scenes from this complete film script. Return ONLY a JSON array with NO explanation.

For EVERY scene in the script, include:
- scene_number: Keep EXACTLY as in script (e.g., "1", "4", "4.1", "4.5", "29", "29.3")
- location: The exact location name
- time_of_day: DAY, NIGHT, DUSK, DAWN, AFTERNOON, etc.
- description: One line summary of what happens

CRITICAL RULES:
1. Extract EVERY scene from the script
2. Do NOT skip any scenes
3. Do NOT rename or renumber scenes
4. Keep original scene numbers exactly as they appear
5. Scene continuations (4.1, 4.2, etc.) are separate scenes
6. Return ONLY valid JSON array, nothing else

COMPLETE SCRIPT:
{script_text}

Return ONLY JSON array starting with [ and ending with ]"""
                
                response_text = await self.llm_client.call_model(prompt, temperature=0.2, max_tokens=16000)
                
                if not response_text or len(response_text) < 10:
                    logger.warning(f"⚠️ AI returned empty response: '{response_text[:100]}'")
                else:
                    extracted_scenes = self._parse_json_safely(response_text)
                    logger.info(f"📊 AI extracted: {len(extracted_scenes)} scenes")
                    
                    if extracted_scenes and len(extracted_scenes) > 0:
                        logger.info(f"✅ AI extraction success: {len(extracted_scenes)} scenes")
                        ai_success = True
                        sample = [str(s.get('scene_number', '?')) for s in extracted_scenes[:10]]
                        logger.info(f"   Sample: {sample}")
                    else:
                        logger.warning(f"⚠️ AI returned empty list or invalid format")
            
            except Exception as e:
                logger.error(f"❌ AI call failed: {type(e).__name__}: {str(e)[:100]}")
        
        # ═══ PHASE 2: FALLBACK TO REGEX ═══
        if not ai_success or len(extracted_scenes) == 0:
            logger.info("📊 Using regex fallback extraction...")
            regex_scenes = self._extract_scenes_regex(script_text)
            extracted_scenes = regex_scenes
            logger.info(f"📊 Regex extracted: {len(regex_scenes)} scenes")
        
        # ═══ PHASE 3: VALIDATE ═══
        validated_scenes = self._validate_scenes(extracted_scenes)
        
        logger.info(f"🎬 SceneExtractor FINAL: {len(validated_scenes)} scenes")
        if validated_scenes:
            sample_nums = [str(s['scene_number']) for s in validated_scenes[:15]]
            logger.info(f"   Scene numbers: {sample_nums}")
        
        return {
            "scenes": validated_scenes,
            "ai_used": ai_success,
            "confidence": 0.95 if ai_success else 0.85,
            "agent_name": "SceneExtractorAgent",
            "count": len(validated_scenes)
        }
    
    def _parse_json_safely(self, response_text):
        """Safely extract JSON from Gemini response"""
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        return []
    
    def _extract_scenes_regex(self, script_text: str) -> List[Dict]:
        """Multi-pattern regex for screenplay formats - PRESERVE ORIGINAL SCENE NUMBERS"""
        scenes = []
        sequential_number = 0
        seen_scene_numbers = set()  # ← DEDUPLICATION!
        
        # Pattern 1: PRIMARY - Numbered scenes "29.5 INT. LOCATION - TIME"
        # MUST have INT/EXT and location, optionally preceded by number
        pattern_numbered = r"^(\d+(?:\.\d+)*)\s*\.?\s+(INT|EXT|INT/EXT)\s*\.?\s+([A-Z][^-\n]+?)(?:\s*[-–]\s*([^\n]+))?$"
        
        # Pattern 2: Standard "INT. LOCATION - TIME" (NO number prefix)
        # Ensure it starts with INT/EXT and has proper structure
        pattern_standard = r"^(INT|EXT|INT/EXT)\s*\.?\s+([A-Z][^-\n]+?)\s*[-–]\s*([^\n]+)$"
        
        # Pattern 3: Minimal "INT. LOCATION" (short, NO time, NO number)
        # Only match if line is actually short
        pattern_minimal = r"^(INT|EXT|INT/EXT)\s*\.?\s+([A-Z][^\n]+?)$"
        
        lines = script_text.split('\n')
        logger.info(f"🔍 Regex: Processing {len(lines)} lines for scene extraction")
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 5:  # Increased minimum length
                continue
            
            # ═══ PATTERN 1: Numbered scenes (HIGHEST PRIORITY) ═══
            match = re.match(pattern_numbered, line, re.IGNORECASE)
            if match:
                scene_num = match.group(1)
                
                # DEDUPLICATION CHECK
                if scene_num in seen_scene_numbers:
                    logger.debug(f"⚠️ Skipping duplicate scene number: {scene_num}")
                    continue
                
                seen_scene_numbers.add(scene_num)
                location = match.group(3).strip()
                time_of_day = match.group(4).strip() if match.group(4) else "DAY"
                
                scenes.append({
                    "scene_number": scene_num,
                    "location": location,
                    "time_of_day": time_of_day,
                    "description": line,
                    "confidence": 0.98,
                    "is_continuation": "." in scene_num
                })
                logger.debug(f"✅ [P1] Scene {scene_num}: {location}")
                continue
            
            # ═══ PATTERN 2: Standard scenes with time (MIDDLE PRIORITY) ═══
            match = re.match(pattern_standard, line, re.IGNORECASE)
            if match:
                # Only create sequential number for non-numbered scenes
                sequential_number += 1
                scene_num = sequential_number
                
                if scene_num in seen_scene_numbers:
                    logger.debug(f"⚠️ Skipping duplicate sequential number: {scene_num}")
                    sequential_number -= 1  # Don't consume the number
                    continue
                
                seen_scene_numbers.add(scene_num)
                location = match.group(2).strip()
                time_of_day = match.group(3).strip()
                
                scenes.append({
                    "scene_number": scene_num,
                    "location": location,
                    "time_of_day": time_of_day,
                    "description": line,
                    "confidence": 0.90,
                    "is_continuation": False
                })
                logger.debug(f"✅ [P2] Scene {scene_num}: {location}")
                continue
            
            # ═══ PATTERN 3: Minimal format (LOW PRIORITY - only short lines) ═══
            if len(line) < 100:  # Be more conservative
                match = re.match(pattern_minimal, line, re.IGNORECASE)
                if match:
                    sequential_number += 1
                    scene_num = sequential_number
                    
                    if scene_num in seen_scene_numbers:
                        sequential_number -= 1
                        continue
                    
                    seen_scene_numbers.add(scene_num)
                    location = match.group(2).strip()
                    
                    scenes.append({
                        "scene_number": scene_num,
                        "location": location,
                        "time_of_day": "DAY",
                        "description": line,
                        "confidence": 0.70,
                        "is_continuation": False
                    })
                    logger.debug(f"✅ [P3] Scene {scene_num}: {location}")
        
        logger.info(f"📊 Regex extraction complete: {len(scenes)} unique scenes")
        logger.info(f"   Total lines processed: {len(lines)}")
        logger.info(f"   Seen scene numbers: {len(seen_scene_numbers)}")
        
        if scenes:
            sample_numbers = [str(s.get('scene_number')) for s in scenes[:15]]
            logger.info(f"   First 15 scene numbers: {sample_numbers}")
        
        return scenes
    
    def _validate_scenes(self, scenes):
        """Validate extracted scenes and preserve original script numbering"""
        validated = []
        
        if not scenes:
            logger.warning("⚠️ No scenes to validate")
            return validated
        
        for scene in scenes:
            # Ensure required fields exist, but preserve original scene_number
            if 'scene_number' not in scene:
                logger.warning(f"⚠️ Scene missing scene_number, skipping")
                continue
            
            scene.setdefault('location', 'Unknown Location')
            scene.setdefault('time_of_day', 'DAY')
            scene.setdefault('confidence', 0.8)
            scene.setdefault('is_continuation', False)
            
            validated.append(scene)
        
        logger.info(f"✅ Validated {len(validated)} scenes with original numbering preserved")
        logger.info(f"   Scene numbers: {[s['scene_number'] for s in validated[:10]]}")
        
        return validated


# ════════════════════════════════════════════════════════════════
# AGENT 2: RISK SCORER
# ════════════════════════════════════════════════════════════════

class RiskScorerAgent:
    """Analyze risks with AI for high-risk scenes + templates for others"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def analyze_risks(self, scenes: List[Dict]) -> Dict[str, Any]:
        """TRY: LLM for high-risk → FALLBACK: Templates"""
        
        # Estimate risks for triage
        risk_estimates = {}
        for scene in scenes:
            risk_keywords = ['stunt', 'body', 'death', 'graveyard', 'burial', 'chase', 'crash', 'fight', 'fire']
            base_risk = 35
            desc = str(scene).lower()
            if any(kw in desc for kw in risk_keywords):
                base_risk = 70
            if 'night' in scene.get('time_of_day', '').lower():
                base_risk += 15
            risk_estimates[scene.get('scene_number', 0)] = min(100, base_risk)
        
        high_risk_scenes = [s for s in scenes if risk_estimates.get(s.get('scene_number', 0), 0) > 50]
        risk_results = []
        ai_used = False
        
        # ═══ PHASE 1: TRY AI FOR HIGH-RISK ═══
        if self.llm_client and len(high_risk_scenes) > 0:
            try:
                logger.info(f"📞 RiskScorer: Calling LLM for {len(high_risk_scenes)} HIGH-RISK scenes...")
                
                prompt = f"""
                Analyze these {len(high_risk_scenes)} HIGH-RISK scenes for production risks:
                {json.dumps(high_risk_scenes[:5], indent=2)}
                
                Return JSON array. For each scene include:
                - scene_number: <int>
                - total_risk_score: <0-100>
                - safety_score: <0-100>
                - logistics_score: <0-100>
                - schedule_score: <0-100>
                - budget_score: <0-100>
                - risk_drivers: ["<driver1>", "<driver2>"]
                - recommendations: ["<action1>", "<action2>"]
                
                Consider:
                - Stunts, action, special effects
                - Night shoots in remote areas
                - Crowd/extras handling
                - Weather dependency
                - Indian production context (permits, logistics)
                """
                
                response_text = await self.llm_client.call_model(prompt, temperature=0.4)
                ai_scores = self._parse_json_safely(response_text)
                
                if ai_scores and len(ai_scores) > 0:
                    logger.info(f"✅ RiskScorer AI success: {len(ai_scores)} high-risk scenes analyzed")
                    risk_results.extend(ai_scores)
                    ai_used = True
            
            except Exception as e:
                logger.warning(f"⚠️ RiskScorer AI failed: {str(e)}, using templates")
        
        # ═══ PHASE 2: FALLBACK TO TEMPLATES ═══
        for scene in scenes:
            if not any(r.get('scene_number') == scene.get('scene_number') for r in risk_results):
                scene_num = scene.get('scene_number', 0)
                base_risk = risk_estimates.get(scene_num, 35)
                risk_results.append({
                    "scene_number": scene_num,
                    "total_risk_score": base_risk,
                    "safety_score": max(0, base_risk - 20),
                    "logistics_score": 15 if base_risk > 50 else 5,
                    "schedule_score": 10 if 'night' in scene.get('time_of_day', '').lower() else 5,
                    "budget_score": 20 if base_risk > 50 else 10,
                    "risk_drivers": ["complexity"] if base_risk > 50 else ["standard"],
                    "recommendations": ["Standard safety protocols"] if base_risk <= 50 else ["Specialized safety coordinator required"]
                })
        
        return {
            "risks": risk_results,
            "high_risk_count": len(high_risk_scenes),
            "ai_used": ai_used,
            "confidence": 0.88 if ai_used else 0.70,
            "agent_name": "RiskScorerAgent"
        }
    
    def _parse_json_safely(self, response_text):
        """Safely extract JSON from Gemini response"""
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        return []


# ════════════════════════════════════════════════════════════════
# AGENT 3: BUDGET ESTIMATOR
# ════════════════════════════════════════════════════════════════

class BudgetEstimatorAgent:
    """Estimate budgets with AI for complex scenes + rate card for others"""
    
    def __init__(self, llm_client, rate_card_df=None):
        self.llm_client = llm_client
        self.rate_card_df = rate_card_df
    
    async def estimate_budget(self, scenes: List[Dict]) -> Dict[str, Any]:
        """TRY: LLM → FALLBACK: Rate card"""
        
        budgets = []
        ai_used = False
        
        # Identify complex scenes for AI
        complex_scenes = [s for s in scenes if self._is_complex(s)]
        
        # ═══ PHASE 1: TRY AI FOR COMPLEX ═══
        if self.llm_client and len(complex_scenes) > 0:
            try:
                logger.info(f"📞 BudgetEstimator: Calling LLM for {len(complex_scenes)} complex scenes...")
                
                prompt = f"""
                Estimate budgets for these {len(complex_scenes)} COMPLEX film scenes (Indian production):
                {json.dumps(complex_scenes[:5], indent=2)}
                
                Return JSON array. For each scene include:
                - scene_number: <int>
                - cost_min: <int>
                - cost_likely: <int>
                - cost_max: <int>
                - line_items: [{{"department": "<name>", "cost": <int>, "reasoning": "<why>"}}]
                - volatility_drivers: ["<driver>"]
                
                Consider:
                - Department costs (Production, Equipment, Safety, Permits, Crew)
                - Location complexity
                - Permit costs/timelines (India: 2-4 weeks)
                - Monsoon/weather impact
                - Contingency (15-25%)
                """
                
                response_text = await self.llm_client.call_model(prompt, temperature=0.4)
                ai_budgets = self._parse_json_safely(response_text)
                
                if ai_budgets and len(ai_budgets) > 0:
                    logger.info(f"✅ BudgetEstimator AI success: {len(ai_budgets)} scenes")
                    budgets.extend(ai_budgets)
                    ai_used = True
            
            except Exception as e:
                logger.warning(f"⚠️ BudgetEstimator AI failed: {str(e)}, using templates")
        
        # ═══ PHASE 2: FALLBACK TO TEMPLATES ═══
        for scene in scenes:
            if not any(b.get('scene_number') == scene.get('scene_number') for b in budgets):
                budgets.append(self._estimate_from_templates(scene))
        
        return {
            "budgets": budgets,
            "total_likely": sum(b.get('cost_likely', 0) for b in budgets),
            "ai_used": ai_used,
            "confidence": 0.80 if ai_used else 0.70,
            "agent_name": "BudgetEstimatorAgent"
        }
    
    def _is_complex(self, scene):
        """Determine if scene is complex"""
        complex_keywords = ['stunt', 'chase', 'night', 'graveyard', 'crowd', 'effect']
        return any(kw in str(scene).lower() for kw in complex_keywords)
    
    def _estimate_from_templates(self, scene):
        """Use template budget estimation"""
        base = 50000
        if 'night' in scene.get('time_of_day', '').lower():
            base += 10000
        return {
            "scene_number": scene.get('scene_number', 0),
            "cost_min": int(base * 0.8),
            "cost_likely": base,
            "cost_max": int(base * 1.5),
            "line_items": [
                {"department": "Production", "cost": int(base * 0.4), "reasoning": "Crew and logistics"},
                {"department": "Equipment", "cost": int(base * 0.3), "reasoning": "Cameras and gear"},
                {"department": "Safety", "cost": int(base * 0.2), "reasoning": "Safety personnel"},
                {"department": "Permits", "cost": int(base * 0.1), "reasoning": "Local permits"}
            ],
            "volatility_drivers": ["weather", "permits"]
        }
    
    def _parse_json_safely(self, response_text):
        """Safely extract JSON"""
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        return []


# ════════════════════════════════════════════════════════════════
# AGENT 4: CROSS-SCENE AUDITOR
# ════════════════════════════════════════════════════════════════

class CrossSceneAuditorAgent:
    """Find cross-scene patterns with AI + rule-based fallback"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def find_insights(self, scenes: List[Dict], risks: List[Dict]) -> Dict[str, Any]:
        """TRY: LLM patterns → FALLBACK: Rule-based"""
        
        insights = []
        ai_used = False
        
        high_risk_scenes = [s for s in scenes if any(r.get('scene_number') == s.get('scene_number') and r.get('total_risk_score', 0) > 50 for r in risks)]
        
        # ═══ PHASE 1: TRY AI FOR PATTERNS ═══
        if self.llm_client and len(high_risk_scenes) >= 2:
            try:
                logger.info("📞 CrossSceneAuditor: Calling LLM for pattern analysis...")
                
                prompt = f"""
                Analyze cross-scene patterns in this film production:
                - Total scenes: {len(scenes)}
                - High-risk scenes: {len(high_risk_scenes)}
                - Scenes: {json.dumps(high_risk_scenes, indent=2)}
                
                Identify patterns:
                1. Location clustering
                2. Risk amplification (consecutive high-risk)
                3. Resource bottlenecks
                4. Budget concentration
                5. Schedule risks
                
                Return JSON array. For each pattern include:
                - pattern_type: <string>
                - scene_ids: [<int>, ...]
                - problem: "<description>"
                - recommendation: "<action>"
                - confidence: <0.0-1.0>
                """
                
                response_text = await self.llm_client.call_model(prompt, temperature=0.4)
                ai_insights = self._parse_json_safely(response_text)
                
                if ai_insights and len(ai_insights) > 0:
                    logger.info(f"✅ CrossSceneAuditor AI success: {len(ai_insights)} patterns")
                    insights.extend(ai_insights)
                    ai_used = True
            
            except Exception as e:
                logger.warning(f"⚠️ CrossSceneAuditor AI failed: {str(e)}, using rules")
        
        # ═══ PHASE 2: FALLBACK TO RULES ═══
        if not ai_used or len(insights) < 2:
            rule_insights = self._find_patterns_by_rules(scenes, risks)
            for insight in rule_insights:
                if not any(i.get('scene_ids') == insight.get('scene_ids') for i in insights):
                    insights.append(insight)
        
        # ═══ PHASE 3: VALIDATE SCENE REFERENCES ═══
        valid_scene_numbers = {s.get('scene_number') for s in scenes}
        insights = [i for i in insights if all(sid in valid_scene_numbers for sid in i.get('scene_ids', []))]
        
        return {
            "insights": insights,
            "ai_used": ai_used,
            "confidence": 0.85 if ai_used else 0.70,
            "agent_name": "CrossSceneAuditorAgent"
        }
    
    def _find_patterns_by_rules(self, scenes, risks):
        """Rule-based pattern detection"""
        insights = []
        
        high_risk_scenes = [s for s in scenes if any(r.get('scene_number') == s.get('scene_number') and r.get('total_risk_score', 0) > 50 for r in risks)]
        
        if len(high_risk_scenes) >= 2:
            insights.append({
                "pattern_type": "risk_concentration",
                "scene_ids": [s.get('scene_number') for s in high_risk_scenes],
                "problem": f"{len(high_risk_scenes)} high-risk scenes require coordinated planning",
                "recommendation": "Consolidate high-risk scenes into same production block",
                "confidence": 0.80
            })
        
        # Location clustering
        locations = {}
        for scene in scenes:
            loc = scene.get('location', 'Unknown')
            if loc not in locations:
                locations[loc] = []
            locations[loc].append(scene.get('scene_number'))
        
        for loc, scene_ids in locations.items():
            if len(scene_ids) > 2:
                insights.append({
                    "pattern_type": "location_cluster",
                    "scene_ids": scene_ids,
                    "problem": f"{len(scene_ids)} scenes at {loc}",
                    "recommendation": "Shoot all scenes at this location consecutively",
                    "confidence": 0.75
                })
        
        return insights
    
    def _parse_json_safely(self, response_text):
        """Safely extract JSON"""
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        return []


# ════════════════════════════════════════════════════════════════
# AGENT 5: MITIGATION PLANNER
# ════════════════════════════════════════════════════════════════

class MitigationPlannerAgent:
    """Generate recommendations with AI + templates"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def generate_recommendations(self, scenes, risks, insights) -> Dict[str, Any]:
        """TRY: LLM recommendations → FALLBACK: Templates"""
        
        recommendations = []
        ai_used = False
        
        high_risk = [r for r in risks if r.get('total_risk_score', 0) > 60]
        
        # ═══ PHASE 1: TRY AI ═══
        if self.llm_client and len(high_risk) > 0:
            try:
                logger.info("📞 MitigationPlanner: Calling LLM for recommendations...")
                
                prompt = f"""
                Generate mitigation recommendations for this film production:
                - High-risk scenes: {len(high_risk)}
                - Cross-scene insights: {len(insights)}
                
                Return JSON array. For each recommendation include:
                - priority: <CRITICAL|HIGH|MEDIUM>
                - recommendation: "<specific action>"
                - budget_impact: "<cost or savings>"
                - risk_reduction: "<percentage>"
                - timeline: "<implementation time>"
                
                Focus on Indian production context (permits, logistics, safety).
                """
                
                response_text = await self.llm_client.call_model(prompt, temperature=0.4)
                recommendations = self._parse_json_safely(response_text)
                
                if recommendations and len(recommendations) > 0:
                    logger.info(f"✅ MitigationPlanner AI success: {len(recommendations)} recommendations")
                    ai_used = True
            
            except Exception as e:
                logger.warning(f"⚠️ MitigationPlanner AI failed: {str(e)}, using templates")
        
        # ═══ PHASE 2: FALLBACK TO TEMPLATES ═══
        if not ai_used or len(recommendations) == 0:
            recommendations = self._generate_template_recommendations(risks, insights)
        
        return {
            "recommendations": recommendations,
            "ai_used": ai_used,
            "confidence": 0.80 if ai_used else 0.70,
            "agent_name": "MitigationPlannerAgent"
        }
    
    def _generate_template_recommendations(self, risks, insights):
        """Template-based recommendations"""
        recommendations = []
        
        high_risk_count = len([r for r in risks if r.get('total_risk_score', 0) > 50])
        
        if high_risk_count > 0:
            recommendations.append({
                "priority": "CRITICAL",
                "recommendation": f"Allocate experienced stunt coordinator for {high_risk_count} high-risk scenes",
                "budget_impact": f"${high_risk_count * 15000:,}",
                "risk_reduction": "35%",
                "timeline": "Immediate"
            })
        
        if len(insights) > 0:
            recommendations.append({
                "priority": "HIGH",
                "recommendation": "Consolidate high-risk scenes into production blocks",
                "budget_impact": "Savings $25,000",
                "risk_reduction": "25%",
                "timeline": "Planning phase"
            })
        
        recommendations.append({
            "priority": "MEDIUM",
            "recommendation": "Establish 15% contingency reserve",
            "budget_impact": "Recommended allocation",
            "risk_reduction": "Budget control",
            "timeline": "Before production"
        })
        
        return recommendations
    
    def _parse_json_safely(self, response_text):
        """Safely extract JSON"""
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        return []


# ════════════════════════════════════════════════════════════════
# ORCHESTRATOR: Coordinate All 5 Agents
# ════════════════════════════════════════════════════════════════

class FullAIEnhancedOrchestrator:
    """
    Orchestrates all 5 agents with AI-first strategy + Safe fallbacks
    Maximum production-readiness for hackathon
    """
    
    def __init__(self, gemini_client=None):
        """Initialize with best available LLM (Qwen3 VI 4B or Gemini)"""
        from app.config import settings
        
        # Determine which LLM to use
        if settings.llm_provider == "qwen3":
            try:
                from app.utils.llm_client import Qwen3Client
                self.llm_client = Qwen3Client(
                    base_url=settings.qwen3_base_url,
                    model=settings.qwen3_model
                )
                logger.info(f"✅ FullAIOrchestrator: Using Qwen3 VI 4B at {settings.qwen3_base_url}")
            except Exception as e:
                logger.warning(f"❌ Qwen3 init failed: {e}, falling back to Gemini")
                self.llm_client = gemini_client
        else:
            self.llm_client = gemini_client
            logger.info("✅ FullAIOrchestrator: Using Gemini API")
        
        # Backward compatibility for agent initialization
        self.gemini_client = self.llm_client
        self.safety_layer = AIAgentSafetyLayer()
    
    async def run_pipeline_full_ai(self, project_id: str, script_text: str) -> Dict[str, Any]:
        """Complete pipeline: Tier 1 → Tier 2 → Tier 3 with AI"""
        
        logger.info("🚀 FULL AI PIPELINE STARTING")
        
        # ═══ TIER 1: EXTRACT SCENES ═══
        logger.info("⏸️ TIER 1: Scene Extraction (AI + Regex fallback)")
        extractor = SceneExtractorAgent(self.gemini_client)
        extraction_result = await self.safety_layer.execute_with_safety(
            extractor, 'extract_scenes', script_text
        )
        scenes = extraction_result['scenes']
        logger.info(f"✅ Extracted {len(scenes)} scenes (AI: {extraction_result['ai_used']})")
        
        # ═══ TIER 2: ANALYZE RISKS ═══
        logger.info("⏸️ TIER 2: Risk Analysis (AI for high-risk, templates for others)")
        risk_scorer = RiskScorerAgent(self.gemini_client)
        risk_result = await self.safety_layer.execute_with_safety(
            risk_scorer, 'analyze_risks', scenes
        )
        risks = risk_result['risks']
        logger.info(f"✅ Analyzed risks (AI: {risk_result['ai_used']})")
        
        # ═══ TIER 2B: BUDGET ESTIMATION ═══
        logger.info("⏸️ TIER 2B: Budget Estimation (AI for complex, templates for others)")
        budget_estimator = BudgetEstimatorAgent(self.gemini_client)
        budget_result = await self.safety_layer.execute_with_safety(
            budget_estimator, 'estimate_budget', scenes
        )
        budgets = budget_result['budgets']
        logger.info(f"✅ Estimated budgets (AI: {budget_result['ai_used']})")
        
        # ═══ TIER 3: CROSS-SCENE INSIGHTS ═══
        logger.info("⏸️ TIER 3: Cross-Scene Intelligence (AI + Rule-based patterns)")
        auditor = CrossSceneAuditorAgent(self.gemini_client)
        insights_result = await self.safety_layer.execute_with_safety(
            auditor, 'find_insights', scenes, risks
        )
        insights = insights_result['insights']
        logger.info(f"✅ Found {len(insights)} insights (AI: {insights_result['ai_used']})")
        
        # ═══ TIER 3B: MITIGATION PLANNING ═══
        logger.info("⏸️ TIER 3B: Mitigation Planning (AI + Templates)")
        planner = MitigationPlannerAgent(self.gemini_client)
        mitigation_result = await self.safety_layer.execute_with_safety(
            planner, 'generate_recommendations', scenes, risks, insights
        )
        recommendations = mitigation_result['recommendations']
        logger.info(f"✅ Generated {len(recommendations)} recommendations (AI: {mitigation_result['ai_used']})")
        
        # ═══ TIER 4: BUDGET OPTIMIZATION (NEW) ═══
        logger.info("⏸️ TIER 4: Budget Optimization Engine (NEW!)")
        from app.agents.optimization_agents import LocationClustererAgent, StuntLocationAnalyzerAgent, ScheduleOptimizerAgent, DepartmentScalerAgent
        
        # Load rate card for optimization
        rate_card_path = Path(__file__).parent.parent / 'datasets' / 'data' / 'rate_card.csv'
        try:
            rate_card_df = pd.read_csv(rate_card_path)
            logger.info(f"✅ Loaded rate card with {len(rate_card_df)} entries")
        except Exception as e:
            logger.error(f"❌ Failed to load rate card: {e}")
            rate_card_df = pd.DataFrame()
        
        # TIER 4A: Location Clustering
        logger.info("  → Location Clustering...")
        clusterer = LocationClustererAgent(self.llm_client)
        location_result = await self.safety_layer.execute_with_safety(
            clusterer, 'cluster_locations', scenes, rate_card_df
        )
        logger.info(f"✅ Found {location_result.get('clusters_found', 0)} location clusters")
        
        # TIER 4B: Stunt Relocation Analysis
        logger.info("  → Stunt Relocation Analysis...")
        stunt_analyzer = StuntLocationAnalyzerAgent(self.llm_client)
        stunt_result = await self.safety_layer.execute_with_safety(
            stunt_analyzer, 'analyze_stunt_relocations', scenes, risks
        )
        logger.info(f"✅ Found {len(stunt_result.get('stunt_relocations', []))} stunt relocation opportunities")
        
        # TIER 4C: Schedule Optimization
        logger.info("  → Schedule Optimization...")
        scheduler = ScheduleOptimizerAgent(self.llm_client)
        schedule_result = await self.safety_layer.execute_with_safety(
            scheduler, 'optimize_schedule', scenes, location_result.get('location_clusters', [])
        )
        logger.info(f"✅ Created optimized schedule: {schedule_result.get('total_production_days', 0)} production days")
        
        # TIER 4D: Department Scaling
        logger.info("  → Department Scaling...")
        scaler = DepartmentScalerAgent(self.llm_client)
        scaling_result = await self.safety_layer.execute_with_safety(
            scaler, 'scale_departments', scenes, location_result.get('location_clusters', []), rate_card_df
        )
        logger.info(f"✅ Calculated department scaling for {len(scaling_result.get('departments', []))} departments")
        
        # Calculate optimization summary
        total_optimization_savings = (
            location_result.get('total_location_savings', 0) +
            stunt_result.get('total_stunt_savings', 0) +
            scaling_result.get('total_department_savings', 0)
        )
        
        # Calculate original vs optimized budget
        original_budget_likely = sum(b.get('cost_likely', 0) for b in budgets)
        optimized_budget_likely = max(0, original_budget_likely - total_optimization_savings)
        savings_percent = round((total_optimization_savings / original_budget_likely * 100) if original_budget_likely > 0 else 0, 1)
        
        # Schedule savings
        original_schedule_days = len(scenes)  # Worst case
        optimized_schedule_days = schedule_result.get('total_production_days', original_schedule_days)
        schedule_savings_percent = round((1 - optimized_schedule_days / max(original_schedule_days, 1)) * 100, 1)
        
        executive_summary = {
            "original_budget_min": sum(b.get('cost_min', 0) for b in budgets),
            "original_budget_likely": original_budget_likely,
            "original_budget_max": sum(b.get('cost_max', 0) for b in budgets),
            "optimized_budget_min": max(0, sum(b.get('cost_min', 0) for b in budgets) - total_optimization_savings),
            "optimized_budget_likely": optimized_budget_likely,
            "optimized_budget_max": max(0, sum(b.get('cost_max', 0) for b in budgets) - total_optimization_savings),
            "total_savings": total_optimization_savings,
            "savings_percent": savings_percent,
            "schedule_original_days": original_schedule_days,
            "schedule_optimized_days": optimized_schedule_days,
            "schedule_savings_percent": schedule_savings_percent,
            "roi_statement": f"Budget optimized by {savings_percent}% (₹{total_optimization_savings:,}) and schedule compressed by {schedule_savings_percent}% ({original_schedule_days} → {optimized_schedule_days} days). Direct ROI through consolidation and smart scheduling."
        }
        
        logger.info(f"💰 OPTIMIZATION SUMMARY: ₹{total_optimization_savings:,} savings ({savings_percent}%) + {schedule_savings_percent}% schedule compression")
        
        # ═══ FINAL ASSEMBLY ═══
        enhanced_output = {
            "run_id": str(uuid.uuid4()),
            "project_id": project_id,
            "status": "completed",
            "analysis_metadata": {
                "analysis_type": "Full AI-Enhanced Production Analysis with Budget Optimization",
                "methodology": "9-Agent Pipeline: 5 Core Analysis Agents + 4 Optimization Agents with Safe Fallbacks",
                "agents_used": [
                    "SceneExtractorAgent (AI + Regex)",
                    "RiskScorerAgent (AI for high-risk + Templates)",
                    "BudgetEstimatorAgent (AI for complex + Templates)",
                    "CrossSceneAuditorAgent (AI + Rules)",
                    "MitigationPlannerAgent (AI + Templates)",
                    "LocationClustererAgent (Budget Optimization)",
                    "StuntLocationAnalyzerAgent (Budget Optimization)",
                    "ScheduleOptimizerAgent (Budget Optimization)",
                    "DepartmentScalerAgent (Budget Optimization)"
                ],
                "ai_success_rate": sum([
                    extraction_result['ai_used'],
                    risk_result['ai_used'],
                    budget_result['ai_used'],
                    insights_result['ai_used'],
                    mitigation_result['ai_used']
                ]) / 5 * 100,
                "agents_ai_enabled": [
                    extraction_result['ai_used'],
                    risk_result['ai_used'],
                    budget_result['ai_used'],
                    insights_result['ai_used'],
                    mitigation_result['ai_used']
                ],
                "safety_fallbacks_active": True,
                "indian_context_aware": True,
                "budget_optimization_enabled": True
            },
            "executive_summary": {
                "total_scenes": len(scenes),
                "high_risk_scenes": len([r for r in risks if r.get('total_risk_score', 0) > 50]),
                "original_budget_likely": original_budget_likely,
                "optimized_budget_likely": optimized_budget_likely,
                "total_savings": total_optimization_savings,
                "savings_percent": savings_percent,
                "schedule_original_days": original_schedule_days,
                "schedule_optimized_days": optimized_schedule_days,
                "schedule_savings_percent": schedule_savings_percent,
                "cross_scene_insights": len(insights),
                "recommendations": len(recommendations),
                "optimization_summary": executive_summary['roi_statement']
            },
            "scenes_analysis": {
                "total_scenes": len(scenes),
                "scenes": scenes,
                "analysis_approach": "AI-extracted with intelligent pattern recognition"
            },
            "risk_intelligence": {
                "risks": risks,
                "high_risk_count": len([r for r in risks if r.get('total_risk_score', 0) > 50]),
                "ai_analyzed": risk_result['ai_used']
            },
            "budget_intelligence": {
                "budgets": budgets,
                "total_likely": sum(b.get('cost_likely', 0) for b in budgets),
                "ai_analyzed": budget_result['ai_used']
            },
            "cross_scene_intelligence": {
                "insights": insights,
                "total_insights": len(insights),
                "ai_analyzed": insights_result['ai_used']
            },
            "production_recommendations": {
                "recommendations": recommendations,
                "ai_analyzed": mitigation_result['ai_used']
            },
            "LAYER_8_location_optimization": location_result,
            "LAYER_9_stunt_optimization": stunt_result,
            "LAYER_10_schedule_optimization": schedule_result,
            "LAYER_11_department_optimization": scaling_result,
            "LAYER_12_executive_summary": executive_summary,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info("🎉 FULL AI PIPELINE COMPLETED")
        return enhanced_output


# Global instance
full_ai_orchestrator = None

def initialize_full_ai_orchestrator(gemini_client=None):
    """Initialize the orchestrator"""
    global full_ai_orchestrator
    full_ai_orchestrator = FullAIEnhancedOrchestrator(gemini_client)
    return full_ai_orchestrator
