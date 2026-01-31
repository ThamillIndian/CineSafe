"""
Constants and enumerations for ShootSafe AI
"""
from enum import Enum

# Risk Amplifier Combinations (Enhancement #2)
RISK_AMPLIFIERS = {
    ("night_shoot", "water", "stunt"): 1.4,        # Worst combo
    ("night_shoot", "crowd", "vehicle"): 1.3,
    ("weather_dependent", "tight_schedule"): 1.25,
    ("international_location", "permits_pending"): 1.2,
    ("water", "animals", "crowd"): 1.3,
    ("stunts", "vehicle_chase", "crowd"): 1.35,
}

# Risk Scale (0-150)
RISK_SCALE_MAX = 150

# Confidence thresholds
CONFIDENCE_THRESHOLD_LOW = 0.8  # Below this, mark as low confidence

# Budget ranges
DEFAULT_BUDGET_VOLATILITY = 0.15  # 15% volatility per low-confidence field

# Schedule parameters
MAX_CONSECUTIVE_NIGHT_SHOOTS = 3
MAX_HEAVY_STUNT_DAYS_PER_WEEK = 2

# Stunt levels
STUNT_LEVELS = ["none", "light", "medium", "heavy"]

# Time of day
TIME_OF_DAY = ["day", "night", "morning", "evening"]

# Permit tiers
PERMIT_TIERS = [1, 2, 3, 4]

# Feature categories
FEATURE_CATEGORIES = {
    "stunt": ["stunt_light", "stunt_medium", "stunt_heavy"],
    "water": ["water_simple", "water_medium", "water_complex"],
    "crowd": ["crowd_small", "crowd_medium", "crowd_large"],
    "vehicle": ["vehicle_simple", "vehicle_medium", "vehicle_heavy"],
    "animal": ["animal_small", "animal_large"],
    "weather": ["weather_dependent"],
    "location": ["location_outdoor", "location_interior", "location_remote"],
    "permit": ["permit_tier_1", "permit_tier_2", "permit_tier_3", "permit_tier_4"],
    "vfx": ["vfx_light", "vfx_medium", "vfx_heavy"],
    "special": ["special_effects", "pyrotechnics"],
}

# LLM Model settings
GEMINI_MAX_RETRIES = 3
GEMINI_REQUEST_TIMEOUT = 60

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Scene extraction fields (all possible fields)
SCENE_EXTRACTION_FIELDS = [
    "location",
    "time_of_day",
    "stunt_level",
    "talent_count",
    "extras_count",
    "water_complexity",
    "vehicle_types",
    "permit_tier",
    "weather_dependent",
    "crowd_size",
    "animals",
    "hazards",
    "location_type",
    "special_effects",
]
