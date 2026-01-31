"""
Unit tests for agents
"""
import pytest
from app.agents.risk_scorer import risk_scorer
from app.agents.budget_estimator import budget_estimator


class TestRiskScorerAgent:
    """Tests for Risk Scorer with Enhancement #2"""
    
    def test_basic_risk_scoring(self):
        """Test basic risk scoring"""
        scene_extraction = {
            "location": {"value": "Mumbai Harbor", "confidence": 0.95},
            "stunt_level": {"value": "heavy", "confidence": 0.85},
            "time_of_day": {"value": "day", "confidence": 0.99},
            "crowd_size": {"value": "small", "confidence": 0.90},
        }
        
        result = risk_scorer.score_scene(scene_extraction)
        
        assert result["final_score"] > 0
        assert result["safety_score"] >= 0
        assert result["final_score"] <= 150
    
    def test_risk_amplification(self):
        """Test Enhancement #2: Risk Amplification"""
        # Scene with dangerous combo: night + water + stunt
        scene_extraction = {
            "location": {"value": "Sea Beach", "confidence": 0.95},
            "stunt_level": {"value": "heavy", "confidence": 0.90},
            "time_of_day": {"value": "night", "confidence": 0.95},
            "water_complexity": {"value": "complex", "confidence": 0.85},
            "crowd_size": {"value": "medium", "confidence": 0.80},
        }
        
        result = risk_scorer.score_scene(scene_extraction)
        
        # Should have amplification applied
        assert result["amplification_factor"] > 1.0
        assert result["amplification_reason"] != ""
        assert "night" in result["amplification_reason"].lower() or "water" in result["amplification_reason"].lower()
    
    def test_no_amplification_for_safe_scene(self):
        """Test that safe scenes have no amplification"""
        scene_extraction = {
            "location": {"value": "Studio", "confidence": 0.99},
            "stunt_level": {"value": "none", "confidence": 0.99},
            "time_of_day": {"value": "day", "confidence": 0.99},
            "crowd_size": {"value": "small", "confidence": 0.95},
        }
        
        result = risk_scorer.score_scene(scene_extraction)
        
        assert result["amplification_factor"] == 1.0
        assert result["final_score"] < 30  # Very safe


class TestBudgetEstimatorAgent:
    """Tests for Budget Estimator with Enhancement #3"""
    
    def test_basic_budget_estimation(self):
        """Test basic budget estimation"""
        scene_extraction = {
            "location": {"value": "Mumbai Harbor", "confidence": 0.95},
            "stunt_level": {"value": "heavy", "confidence": 0.85},
            "time_of_day": {"value": "day", "confidence": 0.99},
            "crowd_size": {"value": "small", "confidence": 0.90},
        }
        
        result = budget_estimator.estimate_scene_budget(
            scene_extraction,
            base_city="Mumbai",
            scale="big_budget"
        )
        
        assert result["cost_likely"] > 0
        assert result["cost_min"] > 0
        assert result["cost_max"] > 0
        assert result["cost_min"] < result["cost_likely"] < result["cost_max"]
    
    def test_uncertainty_ranges(self):
        """Test Enhancement #3: Uncertainty Ranges"""
        # Scene with low confidence on water
        scene_extraction = {
            "location": {"value": "Mumbai Harbor", "confidence": 0.95},
            "stunt_level": {"value": "heavy", "confidence": 0.40},  # LOW CONFIDENCE
            "time_of_day": {"value": "day", "confidence": 0.99},
            "water_complexity": {"value": "complex", "confidence": 0.30},  # LOW CONFIDENCE
        }
        
        result = budget_estimator.estimate_scene_budget(
            scene_extraction,
            base_city="Mumbai",
            scale="big_budget"
        )
        
        # Should have wide range due to low confidence
        cost_range = result["cost_max"] - result["cost_min"]
        assert cost_range > 0
        
        # Should list low-confidence fields as volatility drivers
        assert len(result["volatility_drivers"]) > 0
    
    def test_city_multiplier_effect(self):
        """Test that city multiplier affects budget"""
        scene_extraction = {
            "location": {"value": "Studio", "confidence": 0.99},
            "stunt_level": {"value": "none", "confidence": 0.99},
            "time_of_day": {"value": "day", "confidence": 0.99},
        }
        
        # Same scene, different cities
        result_mumbai = budget_estimator.estimate_scene_budget(
            scene_extraction, "Mumbai", "big_budget"
        )
        
        result_goa = budget_estimator.estimate_scene_budget(
            scene_extraction, "Goa", "big_budget"
        )
        
        # Goa should cost more (1.5x multiplier)
        assert result_goa["cost_likely"] > result_mumbai["cost_likely"]


class TestDatasetLoading:
    """Tests for dataset loading"""
    
    def test_rate_card_loads(self):
        """Test rate_card.csv loads"""
        from app.datasets import dataset_loader
        df = dataset_loader.load_rate_card()
        assert len(df) > 0
        assert "department" in df.columns
        assert "base_cost_min" in df.columns
    
    def test_risk_weights_loads(self):
        """Test risk_weights.csv loads"""
        from app.datasets import dataset_loader
        df = dataset_loader.load_risk_weights()
        assert len(df) > 0
        assert "safety_pts" in df.columns
        assert "logistics_pts" in df.columns
    
    def test_all_datasets_load(self):
        """Test all datasets load successfully"""
        from app.datasets import dataset_loader
        dataset_loader.load_all()
        # Should not raise
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
