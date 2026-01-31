"""
Risk Scoring Agent - Deterministic risk calculation with amplification
ENHANCEMENT #2: Risk Interaction & Compounding
"""
from typing import Dict, List, Any, Tuple
from app.datasets import dataset_loader
from app.utils.constants import RISK_AMPLIFIERS, RISK_SCALE_MAX
import logging

logger = logging.getLogger(__name__)


class RiskScorerAgent:
    """
    Calculates risk scores based on extracted scene features
    Applies risk amplification for dangerous feature combinations
    """
    
    def __init__(self):
        self.risk_weights = dataset_loader.load_risk_weights()
        self.complexity_multipliers = dataset_loader.load_complexity_multipliers()
    
    def score_scene(self, scene_extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk score for a single scene
        
        Args:
            scene_extraction: Extracted scene data with fields and confidence
            
        Returns:
            Risk scores dict with amplification applied
        """
        
        # Step 1: Extract features from extraction
        features = self._extract_features(scene_extraction)
        logger.debug(f"Extracted features: {features}")
        
        # Step 2: Calculate base scores (0-30 per pillar)
        base_scores = self._calculate_base_scores(features)
        base_total = sum(base_scores.values())
        
        logger.debug(f"Base scores: {base_scores}, Total: {base_total}")
        
        # Step 3: Check for risk amplification (ENHANCEMENT #2)
        amplification_factor, amplification_reason = self._get_amplification(features)
        
        # Step 4: Apply amplification
        amplified_delta = base_total * (amplification_factor - 1.0)
        final_total = base_total * amplification_factor
        
        # Step 5: Cap at max scale
        final_total = min(final_total, RISK_SCALE_MAX)
        
        return {
            "base_score": base_total,
            "safety_score": base_scores.get("safety", 0),
            "logistics_score": base_scores.get("logistics", 0),
            "schedule_score": base_scores.get("schedule", 0),
            "budget_score": base_scores.get("budget", 0),
            "compliance_score": base_scores.get("compliance", 0),
            "amplification_factor": amplification_factor,
            "amplification_reason": amplification_reason,
            "amplified_delta": amplified_delta,
            "final_score": int(final_total),
            "risk_drivers": self._identify_drivers(features, base_scores),
        }
    
    def _extract_features(self, scene_extraction: Dict[str, Any]) -> List[str]:
        """
        Extract risk features from scene extraction
        
        Args:
            scene_extraction: Extracted scene data
            
        Returns:
            List of feature strings
        """
        features = []
        
        # Map extraction fields to features
        field_mappings = {
            "stunt_level": {
                "none": [],
                "light": ["stunt_light"],
                "medium": ["stunt_medium"],
                "heavy": ["stunt_heavy"],
            },
            "time_of_day": {
                "day": ["day_shoot"],
                "night": ["night_shoot"],
            },
            "water_complexity": {
                "none": [],
                "simple": ["water_simple"],
                "medium": ["water_medium"],
                "complex": ["water_complex"],
            },
            "crowd_size": {
                "small": ["crowd_small"],
                "medium": ["crowd_medium"],
                "large": ["crowd_large"],
            },
            "vehicle_types": {
                "none": [],
                "simple": ["vehicle_simple"],
                "medium": ["vehicle_medium"],
                "heavy": ["vehicle_heavy"],
            },
            "animals": {
                "none": [],
                "small": ["animal_small"],
                "large": ["animal_large"],
            },
            "weather_dependent": {
                "yes": ["weather_dependent"],
                "no": [],
            },
            "permit_tier": {
                "1": ["permit_tier_1"],
                "2": ["permit_tier_2"],
                "3": ["permit_tier_3"],
                "4": ["permit_tier_4"],
            },
        }
        
        # Extract features from each field
        for field, value_dict in field_mappings.items():
            if field in scene_extraction:
                field_data = scene_extraction[field]
                value = field_data.get("value", "").lower() if isinstance(field_data, dict) else str(field_data).lower()
                
                if value in value_dict:
                    features.extend(value_dict[value])
        
        return features
    
    def _calculate_base_scores(self, features: List[str]) -> Dict[str, int]:
        """
        Calculate base risk scores for each pillar (0-30 each)
        
        Args:
            features: List of feature strings
            
        Returns:
            Dict with safety, logistics, schedule, budget, compliance scores
        """
        scores = {
            "safety": 0,
            "logistics": 0,
            "schedule": 0,
            "budget": 0,
            "compliance": 0,
        }
        
        # Match features against risk_weights.csv
        for feature in features:
            matching_rows = self.risk_weights[self.risk_weights["feature"] == feature]
            
            if not matching_rows.empty:
                row = matching_rows.iloc[0]
                
                # Add points from risk_weights (cap each at 30)
                scores["safety"] = min(scores["safety"] + int(row["safety_pts"]), 30)
                scores["logistics"] = min(scores["logistics"] + int(row["logistics_pts"]), 30)
                scores["schedule"] = min(scores["schedule"] + int(row["schedule_pts"]), 30)
                scores["budget"] = min(scores["budget"] + int(row["budget_pts"]), 30)
                scores["compliance"] = min(scores["compliance"] + int(row["compliance_pts"]), 30)
        
        return scores
    
    def _get_amplification(self, features: List[str]) -> Tuple[float, str]:
        """
        Check for risk amplification based on feature combinations
        ENHANCEMENT #2: Risk Interaction & Compounding
        
        Args:
            features: List of feature strings
            
        Returns:
            Tuple of (amplification_factor, reason_string)
        """
        max_amplifier = 1.0
        amplification_reason = ""
        
        # Check all feature combinations against RISK_AMPLIFIERS
        for combo, amp_factor in RISK_AMPLIFIERS.items():
            # Check if all features in combo are present
            if all(feature in features for feature in combo):
                if amp_factor > max_amplifier:
                    max_amplifier = amp_factor
                    amplification_reason = f"Risk interaction: {' + '.join(combo)}"
                    logger.info(f"⚠️ Risk amplification detected: {amplification_reason} (×{amp_factor})")
        
        return max_amplifier, amplification_reason
    
    def _identify_drivers(self, features: List[str], base_scores: Dict[str, int]) -> List[str]:
        """
        Identify top risk drivers
        
        Args:
            features: List of feature strings
            base_scores: Risk scores dict
            
        Returns:
            List of top risk driver descriptions
        """
        drivers = []
        
        # Add features as drivers
        for feature in features:
            if feature not in ["day_shoot", "location_interior"]:  # Skip low-risk features
                drivers.append(feature)
        
        # Add pillar drivers (those with score >= 15)
        for pillar, score in base_scores.items():
            if score >= 15:
                drivers.append(f"High {pillar} risk ({score} pts)")
        
        return list(set(drivers))  # Remove duplicates


# Global instance
risk_scorer = RiskScorerAgent()
