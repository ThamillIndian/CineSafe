"""
Dataset loading utility - Load all CSV datasets
"""
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DATASETS_DIR = Path(__file__).parent / "data"


class DatasetLoader:
    """Load and cache all datasets"""
    
    _cache = {}
    
    @classmethod
    def load_rate_card(cls) -> pd.DataFrame:
        """Load rate_card.csv"""
        if "rate_card" not in cls._cache:
            path = DATASETS_DIR / "rate_card.csv"
            cls._cache["rate_card"] = pd.read_csv(path)
            logger.info(f"Loaded rate_card: {len(cls._cache['rate_card'])} rows")
        return cls._cache["rate_card"]
    
    @classmethod
    def load_city_multipliers(cls) -> pd.DataFrame:
        """Load city_state_multipliers.csv"""
        if "city_multipliers" not in cls._cache:
            path = DATASETS_DIR / "city_state_multipliers.csv"
            cls._cache["city_multipliers"] = pd.read_csv(path)
            logger.info(f"Loaded city_multipliers: {len(cls._cache['city_multipliers'])} rows")
        return cls._cache["city_multipliers"]
    
    @classmethod
    def load_complexity_multipliers(cls) -> pd.DataFrame:
        """Load complexity_multipliers.csv"""
        if "complexity" not in cls._cache:
            path = DATASETS_DIR / "complexity_multipliers.csv"
            cls._cache["complexity"] = pd.read_csv(path)
            logger.info(f"Loaded complexity_multipliers: {len(cls._cache['complexity'])} rows")
        return cls._cache["complexity"]
    
    @classmethod
    def load_risk_weights(cls) -> pd.DataFrame:
        """Load risk_weights.csv"""
        if "risk_weights" not in cls._cache:
            path = DATASETS_DIR / "risk_weights.csv"
            cls._cache["risk_weights"] = pd.read_csv(path)
            logger.info(f"Loaded risk_weights: {len(cls._cache['risk_weights'])} rows")
        return cls._cache["risk_weights"]
    
    @classmethod
    def load_location_library(cls) -> pd.DataFrame:
        """Load location_library.csv"""
        if "location_library" not in cls._cache:
            path = DATASETS_DIR / "location_library.csv"
            cls._cache["location_library"] = pd.read_csv(path)
            logger.info(f"Loaded location_library: {len(cls._cache['location_library'])} rows")
        return cls._cache["location_library"]
    
    @classmethod
    def load_all(cls):
        """Load all datasets"""
        cls.load_rate_card()
        cls.load_city_multipliers()
        cls.load_complexity_multipliers()
        cls.load_risk_weights()
        cls.load_location_library()
        logger.info("✅ All datasets loaded successfully")
    
    @classmethod
    def clear_cache(cls):
        """Clear cached datasets"""
        cls._cache.clear()
        logger.info("Cache cleared")


# Global instance
dataset_loader = DatasetLoader()
