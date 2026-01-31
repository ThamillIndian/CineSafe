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
    job_id: str
    run_id: str
    status: str
    current_step: str
    progress_percent: int
    current_scene: Optional[int]
    total_scenes: Optional[int]
    error_message: Optional[str]


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
