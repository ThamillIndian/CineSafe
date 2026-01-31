"""
SQLAlchemy ORM models for ShootSafe AI
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, Enum as SQLEnum, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
import enum
import uuid


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ScaleTier(str, enum.Enum):
    INDIE = "indie"
    MID_BUDGET = "mid_budget"
    BIG_BUDGET = "big_budget"


class RunStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class InsightType(str, enum.Enum):
    LOCATION_CHAIN = "location_chain"
    FATIGUE_CLUSTER = "fatigue_cluster"
    TALENT_STRESS = "talent_stress"
    RESOURCE_BOTTLENECK = "resource_bottleneck"
    SCHEDULE_ISSUE = "schedule_issue"


# ============== PROJECTS ==============
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False, default="English")
    base_city = Column(String(100), nullable=False)
    states = Column(JSON, default=list)
    scale = Column(SQLEnum(ScaleTier), default=ScaleTier.MID_BUDGET)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="project")
    runs = relationship("Run", back_populates="project")
    cross_scene_insights = relationship("CrossSceneInsight", back_populates="project")
    decisions = relationship("Decision", back_populates="project")
    assumptions = relationship("Assumption", back_populates="project")
    reports = relationship("Report", back_populates="project")


# ============== DOCUMENTS ==============
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    format = Column(String(20), nullable=False)  # pdf, docx
    text_content = Column(Text)
    page_count = Column(Integer)
    uploaded_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    runs = relationship("Run", back_populates="document")
    
    __table_args__ = (
        Index("idx_project_id", "project_id"),
    )


# ============== RUNS (Pipeline Executions) ==============
class Run(Base):
    __tablename__ = "runs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    run_number = Column(Integer, nullable=False)
    status = Column(SQLEnum(RunStatus), default=RunStatus.QUEUED)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="runs")
    document = relationship("Document", back_populates="runs")
    scenes = relationship("Scene", back_populates="run")
    cross_scene_insights = relationship("CrossSceneInsight", back_populates="run")
    project_summary = relationship("ProjectSummary", back_populates="run", uselist=False)
    jobs = relationship("Job", back_populates="run")
    
    __table_args__ = (
        Index("idx_project_run", "project_id", "run_number"),
    )


# ============== SCENES ==============
class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("runs.id"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    heading = Column(String(255))
    location = Column(String(255))
    raw_text = Column(Text, nullable=False)
    duration_estimated = Column(Float)
    sequence_order = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    run = relationship("Run", back_populates="scenes")
    extractions = relationship("SceneExtraction", back_populates="scene")
    risks = relationship("SceneRisk", back_populates="scene")
    costs = relationship("SceneCost", back_populates="scene")
    decisions = relationship("Decision", back_populates="scene")
    
    __table_args__ = (
        Index("idx_run_scene", "run_id", "scene_number"),
    )


# ============== SCENE EXTRACTIONS ==============
class SceneExtraction(Base):
    __tablename__ = "scene_extractions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scene_id = Column(String(36), ForeignKey("scenes.id"), nullable=False)
    extraction_json = Column(JSON, nullable=False)  # Full extracted data
    confidence_avg = Column(Float)
    low_confidence_fields = Column(JSON, default=list)
    clarification_questions = Column(JSON, default=list)
    extracted_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    scene = relationship("Scene", back_populates="extractions")
    risks = relationship("SceneRisk", back_populates="extraction")
    costs = relationship("SceneCost", back_populates="extraction")


# ============== SCENE RISKS ==============
class SceneRisk(Base):
    __tablename__ = "scene_risks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scene_id = Column(String(36), ForeignKey("scenes.id"), nullable=False)
    extraction_id = Column(String(36), ForeignKey("scene_extractions.id"))
    safety_score = Column(Integer, default=0)
    logistics_score = Column(Integer, default=0)
    schedule_score = Column(Integer, default=0)
    budget_score = Column(Integer, default=0)
    compliance_score = Column(Integer, default=0)
    total_risk_score = Column(Integer, default=0)
    amplification_factor = Column(Float, default=1.0)
    amplification_reason = Column(String(500))
    risk_drivers = Column(JSON, default=list)
    calculated_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    scene = relationship("Scene", back_populates="risks")
    extraction = relationship("SceneExtraction", back_populates="risks")


# ============== SCENE COSTS ==============
class SceneCost(Base):
    __tablename__ = "scene_costs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scene_id = Column(String(36), ForeignKey("scenes.id"), nullable=False)
    extraction_id = Column(String(36), ForeignKey("scene_extractions.id"))
    cost_min = Column(Integer)
    cost_likely = Column(Integer)
    cost_max = Column(Integer)
    line_items = Column(JSON, default=list)
    volatility_drivers = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)
    calculated_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    scene = relationship("Scene", back_populates="costs")
    extraction = relationship("SceneExtraction", back_populates="costs")


# ============== CROSS-SCENE INSIGHTS ==============
class CrossSceneInsight(Base):
    __tablename__ = "cross_scene_insights"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    run_id = Column(String(36), ForeignKey("runs.id"), nullable=False)
    insight_type = Column(SQLEnum(InsightType), nullable=False)
    scene_ids = Column(JSON, default=list)
    problem_description = Column(Text)
    impact_financial = Column(Integer)
    impact_schedule = Column(Float)
    recommendation = Column(Text)
    suggested_reorder = Column(JSON)
    confidence = Column(Float)
    generated_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="cross_scene_insights")
    run = relationship("Run", back_populates="cross_scene_insights")


# ============== PROJECT SUMMARIES ==============
class ProjectSummary(Base):
    __tablename__ = "project_summaries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("runs.id"), nullable=False, unique=True)
    summary_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    run = relationship("Run", back_populates="project_summary")


# ============== JOBS (Worker Progress) ==============
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("runs.id"), nullable=False)
    status = Column(String(50), default="queued")
    current_step = Column(String(255))
    progress_percent = Column(Integer, default=0)
    last_update = Column(DateTime, server_default=func.now(), onupdate=func.now())
    celery_task_id = Column(String(255))
    
    # Relationships
    run = relationship("Run", back_populates="jobs")


# ============== REPORTS ==============
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    run_id = Column(String(36), ForeignKey("runs.id"))
    pdf_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, server_default=func.now())
    file_size = Column(Integer)
    
    # Relationships
    project = relationship("Project", back_populates="reports")


# ============== DECISIONS ==============
class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    scene_id = Column(String(36), ForeignKey("scenes.id"))
    decision_type = Column(String(100))  # what_if_accepted, extraction_corrected, risk_override
    change_from = Column(JSON)
    change_to = Column(JSON)
    reason = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="decisions")
    scene = relationship("Scene", back_populates="decisions")


# ============== ASSUMPTIONS ==============
class Assumption(Base):
    __tablename__ = "assumptions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    assumption_type = Column(String(100))  # budget_cap, max_shoot_days, preferred_cities, no_night_shoots
    value = Column(JSON)
    locked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="assumptions")
