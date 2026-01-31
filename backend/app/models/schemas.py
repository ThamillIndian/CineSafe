"""
Pydantic schemas for API requests/responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ScaleTierEnum(str, Enum):
    INDIE = "indie"
    MID_BUDGET = "mid_budget"
    BIG_BUDGET = "big_budget"


# ============== PROJECT SCHEMAS ==============
class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255)
    language: str = Field("English", max_length=50)
    base_city: str = Field(..., max_length=100)
    states: List[str] = Field(default_factory=list)
    scale: ScaleTierEnum = ScaleTierEnum.MID_BUDGET


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: str
    name: str
    language: str
    base_city: str
    states: List[str]
    scale: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== UPLOAD SCHEMAS ==============
class UploadResponse(BaseModel):
    """Schema for file upload response"""
    document_id: str
    filename: str
    format: str
    page_count: Optional[int]
    uploaded_at: datetime


# ============== RUN SCHEMAS ==============
class RunStartRequest(BaseModel):
    """Schema for starting a pipeline run"""
    mode: str = Field("full_analysis", pattern="^(full_analysis|quick_analysis)$")


class RunStatusResponse(BaseModel):
    """Schema for run status"""
    run_id: str
    document_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    # Optional fields for complex workflows (not used in Option B)
    job_id: Optional[str] = None
    current_step: Optional[str] = None
    progress_percent: Optional[int] = None
    current_scene: Optional[int] = None
    total_scenes: Optional[int] = None
    error_message: Optional[str] = None


# ============== SCENE EXTRACTION SCHEMAS ==============
class SceneExtractionField(BaseModel):
    """Individual field in scene extraction"""
    value: Any
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: Optional[str]
    reasoning: Optional[str]


class SceneExtractionData(BaseModel):
    """Full scene extraction data"""
    location: SceneExtractionField
    time_of_day: SceneExtractionField
    stunt_level: SceneExtractionField
    talent_count: SceneExtractionField
    extras_count: SceneExtractionField
    water_complexity: SceneExtractionField
    vehicle_types: SceneExtractionField
    permit_tier: SceneExtractionField
    weather_dependent: SceneExtractionField
    crowd_size: SceneExtractionField
    animals: SceneExtractionField
    hazards: SceneExtractionField


# ============== RISK SCHEMAS ==============
class RiskScoresResponse(BaseModel):
    """Risk scores response"""
    safety_score: int = Field(ge=0, le=30)
    logistics_score: int = Field(ge=0, le=30)
    schedule_score: int = Field(ge=0, le=30)
    budget_score: int = Field(ge=0, le=30)
    compliance_score: int = Field(ge=0, le=30)
    total_score: int = Field(ge=0, le=150)
    amplification_factor: float
    amplification_reason: Optional[str]
    risk_drivers: List[str]


# ============== BUDGET SCHEMAS ==============
class BudgetLineItem(BaseModel):
    """Individual budget line item"""
    department: str
    cost: int
    multiplier: float
    reason: str


class BudgetEstimate(BaseModel):
    """Budget estimation"""
    cost_min: int
    cost_likely: int
    cost_max: int
    line_items: List[BudgetLineItem]
    volatility_drivers: List[str]
    assumptions: List[str]


# ============== SCENE RESPONSE ==============
class SceneResponse(BaseModel):
    """Full scene response with all data"""
    id: str
    scene_number: int
    location: str
    heading: Optional[str]
    extraction: Optional[SceneExtractionData]
    risk: Optional[RiskScoresResponse]
    budget: Optional[BudgetEstimate]
    confidence: float
    low_confidence_fields: List[str]
    clarification_questions: List[str]


# ============== CROSS-SCENE INSIGHTS ==============
class CrossSceneInsightResponse(BaseModel):
    """Cross-scene insight"""
    id: str
    insight_type: str
    scene_ids: List[int]
    problem_description: str
    impact_financial: Optional[int]
    impact_schedule: Optional[float]
    recommendation: str
    suggested_reorder: Optional[List[int]]
    confidence: float


# ============== DASHBOARD RESULTS ==============
class ProjectSummaryResponse(BaseModel):
    """Complete project dashboard JSON"""
    run_id: str
    total_scenes: int
    total_duration_days: float
    total_budget: Dict[str, int]  # min, likely, max
    risk_summary: Dict[str, int]  # safety, logistics, schedule, budget, compliance, total
    scenes: List[SceneResponse]
    cross_scene_insights: List[CrossSceneInsightResponse]
    uncertainty_flags: List[Dict[str, Any]]
    feasibility_score: float
    producer_summary: str
    generated_at: datetime


# ============== WHAT-IF SCHEMAS ==============
class WhatIfChange(BaseModel):
    """Single what-if change"""
    scene_id: str
    field: str  # stunt_level, time_of_day, location, etc.
    new_value: Any


class WhatIfRequest(BaseModel):
    """What-if simulation request"""
    changes: List[WhatIfChange]


class WhatIfDelta(BaseModel):
    """What-if delta response"""
    cost_delta: int
    schedule_delta: float
    risk_delta: List[int]  # [safety_delta, logistics_delta, schedule_delta, budget_delta, compliance_delta]
    feasibility_delta: float
    affected_insights: List[str]


class WhatIfResponse(BaseModel):
    """Full what-if response"""
    old_state: Dict[str, Any]
    new_state: Dict[str, Any]
    deltas: WhatIfDelta
    feasibility_changed: bool


# ============== OPTIMIZATION SCHEMAS (NEW) ==============
class LocationCluster(BaseModel):
    """Location clustering for optimization"""
    location_name: str
    scene_numbers: List[Any]  # Can be int or str (e.g., "4.1")
    scene_count: int
    unoptimized_days: int
    optimized_days: int
    setup_overhead_original: int
    setup_overhead_optimized: int
    savings: int
    efficiency_percent: float
    recommendation: str


class LocationOptimization(BaseModel):
    """Location clustering results"""
    location_clusters: List[LocationCluster]
    total_location_savings: int
    clusters_found: int
    confidence: float


class StuntRelocation(BaseModel):
    """Stunt relocation recommendation"""
    scene_number: Any
    stunt_description: str
    location_type: str  # PUBLIC, INTERIOR, OUTDOOR
    current_location: str
    public_location_costs: Dict[str, Any]
    studio_alternative: Dict[str, Any]
    recommendation: Dict[str, Any]  # action, savings, reasoning, etc.


class StuntOptimization(BaseModel):
    """Stunt relocation results"""
    stunt_relocations: List[StuntRelocation]
    total_stunt_savings: int
    confidence: float


class DailySchedule(BaseModel):
    """Single day in optimized schedule"""
    day: int
    location: str
    scenes: List[Any]
    shot_type: str
    setup_time_hours: float
    shooting_time_hours: float
    crew_efficiency: str
    notes: Optional[str] = None


class ScheduleOptimization(BaseModel):
    """Optimized shooting schedule"""
    total_shooting_days: int
    total_setup_days: int
    total_production_days: int
    time_savings_percent: float
    daily_breakdown: List[DailySchedule]


class DepartmentScaling(BaseModel):
    """Department cost scaling"""
    department: str
    scale_tier: str
    unoptimized_cost: int
    optimized_cost: int
    savings: int
    scaling_factor: float
    recommendation: str


class DepartmentOptimization(BaseModel):
    """Department scaling results"""
    departments: List[DepartmentScaling]
    total_department_savings: int


class ExecutiveSummary(BaseModel):
    """Executive summary of all optimizations"""
    original_budget_min: int
    original_budget_likely: int
    original_budget_max: int
    optimized_budget_min: int
    optimized_budget_likely: int
    optimized_budget_max: int
    total_savings: int
    savings_percent: float
    schedule_original_days: int
    schedule_optimized_days: int
    schedule_savings_percent: float
    roi_statement: str


class FullResultsResponse(BaseModel):
    """Complete analysis results with optimization layers"""
    run_id: str
    total_scenes: int
    
    # Original analysis layers
    scenes_analysis: Dict[str, Any]
    risk_intelligence: Dict[str, Any]
    budget_intelligence: Dict[str, Any]
    cross_scene_intelligence: Dict[str, Any]
    production_recommendations: Dict[str, Any]
    
    # NEW: Optimization layers
    location_optimization: Optional[LocationOptimization] = None
    stunt_optimization: Optional[StuntOptimization] = None
    schedule_optimization: Optional[ScheduleOptimization] = None
    department_optimization: Optional[DepartmentOptimization] = None
    executive_summary: Optional[ExecutiveSummary] = None
    
    generated_at: datetime
    retrieved_at: datetime
