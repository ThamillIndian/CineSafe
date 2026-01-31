"""
Budget Estimation Agent - Deterministic budget calculation
ENHANCEMENT #3: Confidence & Uncertainty Tracking with ranges
"""
from typing import Dict, List, Any, Tuple
from app.datasets import dataset_loader
from app.utils.constants import CONFIDENCE_THRESHOLD_LOW, DEFAULT_BUDGET_VOLATILITY
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BudgetEstimatorAgent:
    """
    Estimates budget for scenes based on extracted features
    Calculates min/likely/max ranges based on confidence levels
    """
    
    def __init__(self):
        self.rate_card = dataset_loader.load_rate_card()
        self.city_multipliers = dataset_loader.load_city_multipliers()
        self.complexity_multipliers = dataset_loader.load_complexity_multipliers()
    
    def estimate_scene_budget(
        self,
        scene_extraction: Dict[str, Any],
        base_city: str,
        scale: str
    ) -> Dict[str, Any]:
        """
        Estimate budget for a scene
        
        Args:
            scene_extraction: Extracted scene data with confidence scores
            base_city: Base city for multipliers
            scale: Scale tier (indie, mid_budget, big_budget)
            
        Returns:
            Budget dict with min/likely/max and line items
        """
        
        # Step 1: Extract features and confidence
        features = self._extract_features_with_confidence(scene_extraction)
        logger.debug(f"Features with confidence: {features}")
        
        # Step 2: Get city multiplier
        city_multiplier = self._get_city_multiplier(base_city)
        
        # Step 3: Calculate base department costs
        base_costs = self._calculate_base_costs(scale)
        
        # Step 4: Apply feature multipliers
        line_items, total_likely = self._apply_feature_multipliers(
            base_costs, features, city_multiplier, scale
        )
        
        # Step 5: Calculate uncertainty range (ENHANCEMENT #3)
        avg_confidence = self._calculate_avg_confidence(scene_extraction)
        uncertainty_factor = self._calculate_uncertainty(scene_extraction)
        
        cost_min = int(total_likely * (1 - uncertainty_factor))
        cost_max = int(total_likely * (1 + uncertainty_factor))
        cost_likely = int(total_likely)
        
        # Step 6: Identify volatility drivers
        volatility_drivers = self._identify_volatility_drivers(
            scene_extraction, uncertainty_factor
        )
        
        return {
            "cost_min": cost_min,
            "cost_likely": cost_likely,
            "cost_max": cost_max,
            "budget_range": f"₹{cost_min:,} - ₹{cost_max:,}",
            "line_items": line_items,
            "volatility_drivers": volatility_drivers,
            "confidence_avg": round(avg_confidence, 2),
            "assumptions": [
                f"Scale: {scale}",
                f"Base city: {base_city}",
                f"City cost multiplier: {city_multiplier}x",
            ],
        }
    
    def _extract_features_with_confidence(
        self, scene_extraction: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """
        Extract features and their confidence scores
        
        Returns:
            List of (feature_string, confidence) tuples
        """
        features = []
        
        # Map fields to features
        field_mappings = {
            "stunt_level": {
                "none": [],
                "light": [("stunt_light", 1.0)],
                "medium": [("stunt_medium", 1.5)],
                "heavy": [("stunt_heavy", 2.0)],
            },
            "time_of_day": {
                "day": [("day_shoot", 1.0)],
                "night": [("night_shoot", 1.3)],
            },
            "water_complexity": {
                "none": [],
                "simple": [("water_simple", 1.2)],
                "medium": [("water_medium", 1.8)],
                "complex": [("water_complex", 2.5)],
            },
            "crowd_size": {
                "small": [("crowd_small", 1.1)],
                "medium": [("crowd_medium", 1.4)],
                "large": [("crowd_large", 2.0)],
            },
        }
        
        for field, value_dict in field_mappings.items():
            if field in scene_extraction:
                field_data = scene_extraction[field]
                confidence = 0.5
                value = ""
                
                if isinstance(field_data, dict):
                    value = field_data.get("value", "").lower()
                    confidence = field_data.get("confidence", 0.5)
                
                if value in value_dict:
                    for feature, multiplier in value_dict[value]:
                        features.append((feature, confidence))
        
        return features
    
    def _get_city_multiplier(self, base_city: str) -> float:
        """Get city cost multiplier"""
        matching = self.city_multipliers[
            self.city_multipliers["city"] == base_city
        ]
        
        if matching.empty:
            logger.warning(f"City {base_city} not found, using Mumbai (1.0)")
            return 1.0
        
        # Average of all multipliers
        row = matching.iloc[0]
        multipliers = [
            row["labor_multiplier"],
            row["vendor_multiplier"],
            row["permit_complexity_multiplier"],
            row["transport_multiplier"],
            row["lodging_multiplier"],
        ]
        
        return sum(multipliers) / len(multipliers)
    
    def _calculate_base_costs(self, scale: str) -> Dict[str, int]:
        """Calculate base department costs"""
        base_costs = {}
        
        for _, row in self.rate_card.iterrows():
            if row["scale_tier"] == scale:
                dept = row["department"]
                cost_min = row["base_cost_min"]
                cost_max = row["base_cost_max"]
                avg_cost = (cost_min + cost_max) / 2
                
                if dept not in base_costs:
                    base_costs[dept] = int(avg_cost)
        
        return base_costs
    
    def _apply_feature_multipliers(
        self,
        base_costs: Dict[str, int],
        features: List[Tuple[str, float]],
        city_multiplier: float,
        scale: str,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Apply feature multipliers to base costs
        
        Returns:
            Tuple of (line_items, total_cost)
        """
        line_items = []
        total = 0
        
        # Map features to departments
        feature_dept_mapping = {
            "stunt": "Stunt Coordinator",
            "water": "Water Safety Diver",
            "crowd": "Art Department",
            "vehicle": "Transportation",
            "night_shoot": "Lighting Head",
        }
        
        # Calculate line items
        for feature_str, confidence in features:
            multiplier = 1.0
            
            # Find multiplier for this feature
            matching = self.complexity_multipliers[
                self.complexity_multipliers["feature"] == feature_str
            ]
            
            if not matching.empty:
                multiplier = matching.iloc[0]["cost_multiplier"]
            
            # Find appropriate department
            dept = None
            for key, department in feature_dept_mapping.items():
                if key in feature_str:
                    dept = department
                    break
            
            if dept and dept in base_costs:
                cost = int(base_costs[dept] * multiplier * city_multiplier)
                
                line_items.append({
                    "department": dept,
                    "feature": feature_str,
                    "base_cost": base_costs[dept],
                    "multiplier": multiplier,
                    "city_multiplier": city_multiplier,
                    "final_cost": cost,
                    "confidence": confidence,
                })
                
                total += cost
        
        return line_items, total
    
    def _calculate_avg_confidence(self, scene_extraction: Dict[str, Any]) -> float:
        """Calculate average confidence across fields"""
        confidences = []
        
        for field, data in scene_extraction.items():
            if isinstance(data, dict) and "confidence" in data:
                confidences.append(data["confidence"])
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def _calculate_uncertainty(self, scene_extraction: Dict[str, Any]) -> float:
        """
        Calculate budget uncertainty range
        ENHANCEMENT #3: Wider range for low confidence fields
        
        Low confidence = higher volatility in budget
        """
        uncertainty = 0.0
        low_conf_count = 0
        
        for field, data in scene_extraction.items():
            if isinstance(data, dict):
                confidence = data.get("confidence", 0.5)
                
                if confidence < CONFIDENCE_THRESHOLD_LOW:
                    low_conf_count += 1
                    # Each low-confidence field adds volatility
                    volatility_per_field = (1.0 - confidence) * DEFAULT_BUDGET_VOLATILITY
                    uncertainty += volatility_per_field
        
        # Cap uncertainty at 50%
        return min(uncertainty, 0.5)
    
    def _identify_volatility_drivers(
        self, scene_extraction: Dict[str, Any], uncertainty: float
    ) -> List[str]:
        """Identify what's causing budget uncertainty"""
        drivers = []
        
        if uncertainty > 0.0:
            for field, data in scene_extraction.items():
                if isinstance(data, dict):
                    confidence = data.get("confidence", 0.5)
                    
                    if confidence < CONFIDENCE_THRESHOLD_LOW:
                        drivers.append(f"{field} unclear (confidence {confidence:.0%})")
        
        return drivers


# Global instance
budget_estimator = BudgetEstimatorAgent()
