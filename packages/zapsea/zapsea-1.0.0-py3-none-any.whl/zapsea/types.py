"""
ZapSEA Python SDK - Type Definitions

Pydantic models and type definitions for API requests and responses.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .config import ANALYSIS_DEPTHS, IMPACT_DIMENSIONS, SCENARIO_TYPES, TIME_HORIZONS, JOB_STATUSES


class AnalysisDepth(str, Enum):
    """Valid analysis depth values."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    DEEP = "deep"


class ImpactDimension(str, Enum):
    """Valid impact dimension values."""
    ECONOMIC = "economic"
    REGULATORY = "regulatory"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    POLITICAL = "political"


class ScenarioType(str, Enum):
    """Valid scenario type values."""
    OPTIMISTIC = "optimistic"
    REALISTIC = "realistic"
    PESSIMISTIC = "pessimistic"
    WORST_CASE = "worst_case"
    BEST_CASE = "best_case"


class TimeHorizon(str, Enum):
    """Valid time horizon values."""
    THREE_MONTHS = "3_months"
    SIX_MONTHS = "6_months"
    TWELVE_MONTHS = "12_months"
    TWENTY_FOUR_MONTHS = "24_months"
    FIVE_YEARS = "5_years"


class JobStatus(str, Enum):
    """Valid job status values."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SimulationParameters(BaseModel):
    """Parameters for impact simulation."""
    time_horizon: TimeHorizon = TimeHorizon.TWELVE_MONTHS
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    include_uncertainty: bool = True
    focus_areas: Optional[List[str]] = None
    stakeholder_groups: Optional[List[str]] = None
    
    class Config:
        use_enum_values = True


class ImpactSimulationRequest(BaseModel):
    """Request model for impact simulation."""
    policy_description: Optional[str] = None
    policy_id: Optional[str] = None
    analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD
    parameters: SimulationParameters = Field(default_factory=SimulationParameters)
    impact_dimensions: List[ImpactDimension] = Field(default_factory=lambda: [ImpactDimension.ECONOMIC, ImpactDimension.REGULATORY])
    scenario_types: List[ScenarioType] = Field(default_factory=lambda: [ScenarioType.REALISTIC])
    include_visualizations: bool = False
    
    @validator('policy_description', 'policy_id')
    def validate_policy_input(cls, v, values):
        """Ensure either policy_description or policy_id is provided."""
        if not v and not values.get('policy_id') and not values.get('policy_description'):
            raise ValueError('Either policy_description or policy_id must be provided')
        return v
    
    class Config:
        use_enum_values = True


class InfluencePathRequest(BaseModel):
    """Request model for influence pathfinding."""
    source_entity_id: str
    target_entity_id: str
    max_depth: int = Field(default=5, ge=1, le=10)
    include_alternatives: bool = False
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    include_network_stats: bool = False


class StakeholderInfo(BaseModel):
    """Information about a stakeholder."""
    id: str
    name: str
    type: str
    influence_score: float
    stance: Optional[str] = None
    confidence: float


class RiskOpportunity(BaseModel):
    """Risk or opportunity identified in analysis."""
    id: str
    type: str  # "risk" or "opportunity"
    description: str
    probability: float
    impact_magnitude: float
    confidence: float
    mitigation_strategies: Optional[List[str]] = None


class ImpactSimulationResult(BaseModel):
    """Result of an impact simulation."""
    simulation_id: str
    policy_id: Optional[str] = None
    success_probability: float
    confidence_score: float
    total_documents_analyzed: int
    
    # Analysis results
    executive_summary: str
    key_findings: List[str]
    stakeholders: List[StakeholderInfo]
    risks: List[RiskOpportunity]
    opportunities: List[RiskOpportunity]
    
    # Scenario analysis
    scenario_outcomes: Dict[str, Dict[str, Any]]
    
    # Metadata
    analysis_depth: str
    impact_dimensions: List[str]
    created_at: datetime
    processing_time_seconds: float


class InfluencePathResult(BaseModel):
    """Result of influence pathfinding."""
    path_id: str
    source_entity: Dict[str, Any]
    target_entity: Dict[str, Any]
    
    # Path information
    path_length: int
    total_influence_score: float
    confidence_score: float
    
    # Path details
    path_entities: List[Dict[str, Any]]
    path_relationships: List[Dict[str, Any]]
    
    # Alternative paths (if requested)
    alternative_paths: Optional[List[Dict[str, Any]]] = None
    
    # Network statistics (if requested)
    network_stats: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime
    processing_time_seconds: float


class JobInfo(BaseModel):
    """Information about an async job."""
    job_id: str
    job_type: str
    status: JobStatus
    progress_percentage: int = Field(ge=0, le=100)
    
    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results (only present when completed)
    result_data: Optional[Union[ImpactSimulationResult, InfluencePathResult]] = None
    
    # Error information (only present when failed)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Metadata
    estimated_completion_time: Optional[str] = None
    api_version: str = "2.0"
    
    class Config:
        use_enum_values = True


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    page: str
    feedback_type: str = "general"
    feature_used: Optional[str] = None
    
    @validator('comment')
    def validate_comment_length(cls, v):
        """Ensure comment is not too long."""
        if v and len(v) > 1000:
            raise ValueError('Comment must be 1000 characters or less')
        return v


class APIUsage(BaseModel):
    """API usage information."""
    current_period_calls: int
    monthly_quota: int
    requests_per_minute_limit: int
    tier: str
    
    # Usage breakdown
    calls_by_endpoint: Dict[str, int]
    calls_by_day: Dict[str, int]
    
    # Billing information (if applicable)
    billable_calls: Optional[int] = None
    estimated_cost: Optional[float] = None
