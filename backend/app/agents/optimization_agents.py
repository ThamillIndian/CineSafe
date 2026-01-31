"""
Budget Optimization Agents for Film Production Planning
Implements: Location Clustering, Stunt Relocation, Schedule Optimization, Department Scaling
"""
import logging
import json
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)


class LocationClustererAgent:
    """
    Groups scenes by location and calculates consolidation potential
    Deterministic logic first, AI-optional for complex clustering
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        logger.info("[LocationClustererAgent] Initialized")
    
    async def cluster_locations(self, scenes: List[Dict], rate_card_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Group scenes by location and calculate optimization savings
        
        Args:
            scenes: List of scene dictionaries with location, time_of_day, etc.
            rate_card_df: Rate card dataframe for cost lookups
        
        Returns:
            Dictionary with location clusters and total savings
        """
        logger.info(f"[LocationClusterer] Starting clustering for {len(scenes)} scenes")
        
        # Group scenes by location
        location_groups = defaultdict(list)
        for scene in scenes:
            location = scene.get('location', 'Unknown Location')
            location_groups[location].append(scene)
        
        clusters = []
        total_savings = 0
        
        # Setup cost per day (from rate card - lighting head as proxy)
        setup_cost_per_day = 80000  # ₹80K per setup (mid-budget)
        
        for location, scenes_list in location_groups.items():
            if len(scenes_list) >= 2:  # Only clusters with 2+ scenes
                cluster_data = self._analyze_cluster(
                    location,
                    scenes_list,
                    setup_cost_per_day,
                    rate_card_df
                )
                clusters.append(cluster_data)
                total_savings += cluster_data.get('savings', 0)
                
                logger.info(f"  Cluster: {location} ({len(scenes_list)} scenes) - Savings: ₹{cluster_data['savings']:,}")
        
        result = {
            "location_clusters": sorted(clusters, key=lambda x: x['savings'], reverse=True),
            "total_location_savings": total_savings,
            "clusters_found": len(clusters),
            "confidence": 0.92,
            "ai_used": False,
            "reasoning": f"Identified {len(clusters)} location clusters by consolidating scattered scenes"
        }
        
        logger.info(f"[LocationClusterer] Complete: {len(clusters)} clusters, Savings: ₹{total_savings:,}")
        return result
    
    def _analyze_cluster(self, location: str, scenes_list: List[Dict], 
                        setup_cost_per_day: int, rate_card_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze a single location cluster"""
        
        # Calculate days needed
        unoptimized_days = len(scenes_list)  # Each scene shot separately
        
        # Optimization: group by time_of_day, then batch 2-3 scenes per day
        time_groups = defaultdict(list)
        for scene in scenes_list:
            time_of_day = scene.get('extraction', {}).get('time_of_day', {}).get('value', 'DAY')
            time_groups[time_of_day].append(scene)
        
        # Calculate optimized days: ~1.5 scenes per day (realistic)
        # Formula: len(scenes) / 1.5 = len(scenes) * 2 / 3
        optimized_days = max(1, (len(scenes_list) * 2 + 2) // 3)  # ~1.5 scenes per day
        
        # Calculate savings
        unoptimized_overhead = unoptimized_days * setup_cost_per_day
        optimized_overhead = max(setup_cost_per_day, optimized_days * (setup_cost_per_day * 0.6))  # Reduced for continuation days
        savings = int(unoptimized_overhead - optimized_overhead)
        
        scene_numbers = [str(s.get('scene_number', '?')) for s in scenes_list]
        
        return {
            "location_name": location,
            "scene_numbers": scene_numbers,
            "scene_count": len(scenes_list),
            "unoptimized_days": unoptimized_days,
            "optimized_days": optimized_days,
            "setup_overhead_original": unoptimized_overhead,
            "setup_overhead_optimized": int(optimized_overhead),
            "savings": savings,
            "efficiency_percent": round((savings / unoptimized_overhead * 100) if unoptimized_overhead > 0 else 0, 1),
            "recommendation": f"Consolidate to {optimized_days}-day shoot (was {unoptimized_days} days) by batching {optimized_days // len(time_groups) if time_groups else 1} scenes/day"
        }


class StuntLocationAnalyzerAgent:
    """
    Analyzes stunts and recommends moving high-cost public stunts to studios
    Uses risk scoring and location type classification
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        logger.info("[StuntLocationAnalyzerAgent] Initialized")
    
    async def analyze_stunt_relocations(self, scenes: List[Dict], risks: List[Dict]) -> Dict[str, Any]:
        """
        Find high-cost public stunts that can move to studio
        
        Args:
            scenes: List of scene dictionaries
            risks: List of risk analysis results
        
        Returns:
            Dictionary with stunt relocation recommendations
        """
        logger.info(f"[StuntAnalyzer] Analyzing {len(scenes)} scenes for stunt relocations")
        
        stunt_relocations = []
        total_savings = 0
        
        # Create risk lookup
        risk_lookup = {r.get('scene_number'): r for r in risks}
        
        for scene in scenes:
            scene_num = scene.get('scene_number')
            
            # Check if this scene has high stunt level
            extraction = scene.get('extraction', {})
            stunt_level = extraction.get('stunt_level', {}).get('value', 'low')
            
            if stunt_level in ['medium', 'high', 'extreme']:
                location = scene.get('location', 'Unknown')
                location_type = self._classify_location_type(location)
                risk_score = risk_lookup.get(scene_num, {}).get('total_score', 0)
                
                # Flag public locations with medium+ stunts and high risk
                if location_type == 'PUBLIC' and risk_score > 50:
                    relocation = self._generate_relocation_recommendation(
                        scene_num,
                        stunt_level,
                        location,
                        location_type,
                        risk_score
                    )
                    stunt_relocations.append(relocation)
                    total_savings += relocation.get('savings', 0)
                    logger.info(f"  Scene {scene_num}: Recommend studio relocation, Savings: ₹{relocation['savings']:,}")
        
        result = {
            "stunt_relocations": stunt_relocations,
            "total_stunt_savings": total_savings,
            "confidence": 0.85,
            "ai_used": False,
            "reasoning": f"Identified {len(stunt_relocations)} high-risk public stunts that can be moved to controlled studio environments"
        }
        
        logger.info(f"[StuntAnalyzer] Complete: {len(stunt_relocations)} relocations, Savings: ₹{total_savings:,}")
        return result
    
    def _classify_location_type(self, location: str) -> str:
        """Classify location as PUBLIC, INTERIOR, or OUTDOOR"""
        location_lower = location.lower()
        
        public_keywords = ['graveyard', 'street', 'highway', 'city', 'public', 'market', 'forest', 'river', 'bridge', 'beach', 'park']
        interior_keywords = ['office', 'home', 'apartment', 'station', 'lab', 'house', 'room', 'building', 'studio']
        
        for keyword in public_keywords:
            if keyword in location_lower:
                return 'PUBLIC'
        
        for keyword in interior_keywords:
            if keyword in location_lower:
                return 'INTERIOR'
        
        return 'OUTDOOR'
    
    def _generate_relocation_recommendation(self, scene_num: Any, stunt_level: str, 
                                          location: str, location_type: str, risk_score: int) -> Dict[str, Any]:
        """Generate stunt relocation recommendation for a scene"""
        
        # Calculate public location costs
        permits_cost = 150000 if risk_score > 70 else 100000 if risk_score > 50 else 50000
        police_cost = 30000 if risk_score > 70 else 20000
        clearance_cost = 20000
        night_surcharge = 30000 if 'night' in location.lower() else 0
        insurance_surcharge = int((permits_cost + police_cost) * 0.15)
        total_public = permits_cost + police_cost + clearance_cost + night_surcharge + insurance_surcharge
        
        # Calculate studio alternative costs
        set_cost = 40000
        stunt_setup = 25000 if stunt_level == 'extreme' else 15000 if stunt_level == 'high' else 10000
        lighting_cost = 60000
        total_studio = set_cost + stunt_setup + lighting_cost
        
        savings = total_public - total_studio
        
        return {
            "scene_number": scene_num,
            "stunt_description": f"{stunt_level.title()} stunt in {location}",
            "location_type": location_type,
            "current_location": location,
            "public_location_costs": {
                "permits": permits_cost,
                "police_coordination": police_cost,
                "public_clearance": clearance_cost,
                "night_shoot_surcharge": night_surcharge,
                "insurance_premium_15pct": insurance_surcharge,
                "total": total_public
            },
            "studio_alternative": {
                "location_name": f"Studio {location} Set",
                "set_design": set_cost,
                "stunt_equipment": stunt_setup,
                "controlled_lighting": lighting_cost,
                "total": total_studio
            },
            "recommendation": {
                "action": "MOVE TO STUDIO",
                "savings": savings,
                "savings_percent": round((savings / total_public * 100) if total_public > 0 else 0, 1),
                "risk_reduction": "HIGH",
                "reasoning": f"Studio alternative {savings:,} cheaper + eliminates permit complexity + schedule flexibility"
            }
        }


class ScheduleOptimizerAgent:
    """
    Creates optimized shooting schedule based on location clusters and scene grouping
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        logger.info("[ScheduleOptimizerAgent] Initialized")
    
    async def optimize_schedule(self, scenes: List[Dict], location_clusters: List[Dict]) -> Dict[str, Any]:
        """
        Create optimized shooting schedule
        
        Args:
            scenes: List of scenes
            location_clusters: Location cluster data from LocationClustererAgent
        
        Returns:
            Optimized shooting schedule with daily breakdowns
        """
        logger.info(f"[ScheduleOptimizer] Creating optimized schedule")
        
        daily_plan = []
        shot_scenes = set()
        current_day = 0
        
        # Sort clusters by importance (number of scenes, risk level)
        sorted_clusters = sorted(location_clusters, key=lambda x: x['scene_count'], reverse=True)
        
        for cluster in sorted_clusters:
            cluster_scenes = self._get_cluster_scenes(cluster, scenes)
            
            if not cluster_scenes:
                continue
            
            # Split by time_of_day for multi-day clusters
            time_groups = defaultdict(list)
            for scene in cluster_scenes:
                if scene['scene_number'] not in shot_scenes:
                    time_of_day = scene.get('extraction', {}).get('time_of_day', {}).get('value', 'DAY')
                    time_groups[time_of_day].append(scene)
                    shot_scenes.add(scene['scene_number'])
            
            # Create day entries - realistic scene scheduling
            # Complex scenes: 1 per day, Medium: 1.5 per day, Simple: 2 per day
            days_needed = self._calculate_realistic_days(cluster_scenes)
            days_needed = max(1, days_needed)
            
            for day_idx in range(days_needed):
                current_day += 1
                start_idx = day_idx * 2  # 2 scenes per day on average (more realistic)
                end_idx = min(start_idx + 2, len(cluster_scenes))
                day_scenes = cluster_scenes[start_idx:end_idx]
                
                daily_plan.append(self._create_daily_entry(
                    current_day,
                    cluster['location_name'],
                    day_scenes,
                    day_idx == 0  # is_setup_day
                ))
        
        # Add contingency day
        current_day += 1
        daily_plan.append({
            "day": current_day,
            "location": "Various (Reshoots/Contingency)",
            "scenes": ["TBD"],
            "shot_type": "CONTINGENCY",
            "setup_time_hours": 0,
            "shooting_time_hours": 8,
            "crew_efficiency": "HIGH",
            "notes": "Reserve day for reshoots and contingency coverage"
        })
        
        # Calculate realistic schedule savings
        # Realistic baseline: ~1.2 days per scene (without optimization, 120 scenes = ~100 days)
        # This is based on 1-2 scenes per day being the industry standard
        realistic_baseline_days = max(len(scenes) * 0.9, len(scenes))  # Start at ~0.9 days per scene
        optimized_days = current_day
        
        # Cap schedule savings to realistic maximum of 25%
        calculated_savings = round((1 - optimized_days / max(realistic_baseline_days, 1)) * 100, 1)
        schedule_savings = min(calculated_savings, 25.0)  # Cap at 25% max
        
        result = {
            "total_shooting_days": len([d for d in daily_plan if d['shot_type'] != 'CONTINGENCY']),
            "total_setup_days": len([d for d in daily_plan if 'Setup' in d.get('shot_type', '')]),
            "total_production_days": current_day,
            "time_savings_percent": schedule_savings,
            "daily_breakdown": daily_plan,
            "ai_used": False,
            "reasoning": f"Consolidated {len(scenes)} scenes into {optimized_days} production days ({schedule_savings}% compression)"
        }
        
        logger.info(f"[ScheduleOptimizer] Complete: {optimized_days} days (saves {schedule_savings}% vs realistic baseline of {realistic_baseline_days} days)")
        return result
    
    def _calculate_realistic_days(self, scenes: List[Dict]) -> int:
        """
        Calculate realistic production days based on scene complexity
        - Complex/Stunt scenes: 1 per day
        - Medium scenes: 1.5 per day
        - Simple scenes: 2 per day
        Average: ~1.5 scenes per day (realistic for film production)
        """
        total_scenes = len(scenes)
        # Realistic average: 1.5 scenes per day (not 3!)
        realistic_days = max(1, (total_scenes * 2) // 3)  # Equivalent to /1.5
        return realistic_days
    
    def _get_cluster_scenes(self, cluster: Dict, scenes: List[Dict]) -> List[Dict]:
        """Get scene objects for a cluster"""
        cluster_numbers = [str(s) for s in cluster.get('scene_numbers', [])]
        return [s for s in scenes if str(s.get('scene_number')) in cluster_numbers]
    
    def _create_daily_entry(self, day: int, location: str, scenes: List[Dict], is_setup: bool) -> Dict[str, Any]:
        """Create a single day entry in the schedule"""
        scene_numbers = [str(s.get('scene_number')) for s in scenes]
        shot_type = f"Setup + Shooting" if is_setup else "Continuation"
        setup_hours = 8 if is_setup else 0
        shooting_hours = 8 if not is_setup else 4
        
        return {
            "day": day,
            "location": location,
            "scenes": scene_numbers,
            "shot_type": shot_type,
            "setup_time_hours": setup_hours,
            "shooting_time_hours": shooting_hours,
            "crew_efficiency": "HIGH" if is_setup else "MAX",
            "notes": "Full location setup" if is_setup else "Continue shooting without setup"
        }


class DepartmentScalerAgent:
    """
    Calculates department costs based on optimized schedule and clustering
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        logger.info("[DepartmentScalerAgent] Initialized")
    
    async def scale_departments(self, scenes: List[Dict], 
                                location_clusters: List[Dict],
                                rate_card_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate department costs with optimized scaling
        
        Args:
            scenes: List of scenes
            location_clusters: Location cluster data
            rate_card_df: Rate card dataframe
        
        Returns:
            Department scaling results
        """
        logger.info("[DepartmentScaler] Scaling department costs")
        
        # Get relevant departments from rate card
        departments = []
        
        # Calculate scaling factors based on clusters
        num_locations = len(location_clusters)
        num_days = sum(c.get('optimized_days', 1) for c in location_clusters)
        
        # Key departments affected by consolidation
        key_depts = ['Lighting Head', 'Grip', 'Camera Operator', 'Sound Engineer', 'Art Department']
        
        for dept_name in key_depts:
            dept_data = rate_card_df[rate_card_df['department'] == dept_name]
            
            if dept_data.empty:
                continue
            
            # Get mid_budget tier
            mid_tier = dept_data[dept_data['scale_tier'] == 'mid_budget']
            if mid_tier.empty:
                continue
            
            base_min = int(mid_tier.iloc[0]['base_cost_min'])
            base_max = int(mid_tier.iloc[0]['base_cost_max'])
            base_avg = (base_min + base_max) // 2
            
            # Calculate unoptimized vs optimized
            unoptimized = base_avg * num_locations  # Full cost per location
            
            # Optimization factors
            if dept_name in ['Lighting Head', 'Grip']:
                scaling_factor = 0.6  # 40% cost reduction through consolidation
            elif dept_name == 'Camera Operator':
                scaling_factor = 0.7  # 30% reduction
            elif dept_name == 'Sound Engineer':
                scaling_factor = 0.65  # 35% reduction
            else:  # Art Department
                scaling_factor = 0.5  # 50% reduction (shared sets)
            
            optimized = int(base_avg + (unoptimized - base_avg) * scaling_factor)
            savings = unoptimized - optimized
            
            departments.append({
                "department": dept_name,
                "scale_tier": "mid_budget",
                "unoptimized_cost": unoptimized,
                "optimized_cost": optimized,
                "savings": savings,
                "scaling_factor": scaling_factor,
                "recommendation": self._get_dept_recommendation(dept_name, scaling_factor, num_locations)
            })
        
        total_dept_savings = sum(d.get('savings', 0) for d in departments)
        
        result = {
            "departments": sorted(departments, key=lambda x: x['savings'], reverse=True),
            "total_department_savings": total_dept_savings,
            "ai_used": False,
            "reasoning": f"Applied consolidation scaling across {len(departments)} departments"
        }
        
        logger.info(f"[DepartmentScaler] Complete: {len(departments)} departments, Savings: ₹{total_dept_savings:,}")
        return result
    
    def _get_dept_recommendation(self, dept: str, scaling_factor: float, num_locations: int) -> str:
        """Generate department-specific recommendation"""
        if dept == 'Lighting Head':
            return f"Keep gaffer + cinematographer constant, reduce assistants from Day 2 ({(1-scaling_factor)*100:.0f}% savings)"
        elif dept == 'Grip':
            return f"Full grip team for setup day, 1 grip + best boy for continuation ({(1-scaling_factor)*100:.0f}% savings)"
        elif dept == 'Camera Operator':
            return f"DP constant, reduce second camera operator ({(1-scaling_factor)*100:.0f}% savings)"
        elif dept == 'Sound Engineer':
            return f"Boom operator can cover multiple locations ({(1-scaling_factor)*100:.0f}% savings)"
        else:
            return f"Art department minimal overlap between locations ({(1-scaling_factor)*100:.0f}% savings)"
