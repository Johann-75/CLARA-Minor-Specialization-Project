from typing import Literal, List, Optional
from pydantic import BaseModel, Field

class GeminiRecommendationItem(BaseModel):
    instance_id: str = Field(description="Unique cloud instance ID (must strictly match one of the queried input instance IDs)")
    priority: Literal["Critical", "High", "Medium", "Low"] = Field(description="Operational remediation priority level")
    title: str = Field(description="Concise, actionable remediation title (max 10 words)")
    explanation: str = Field(description="Clear explanation citing observed risk scores, telemetry, or security flags")
    recommended_action: str = Field(description="Specific operational step-by-step remediation procedure")
    expected_benefit: str = Field(description="Quantified or directional risk, posture, or cost improvement")
    estimated_savings_usd: float = Field(default=0.0, description="Projected monthly USD cost savings")
    estimated_effort_hours: float = Field(default=1.0, description="Estimated engineering effort in hours")
    # Optional un-trusted model declarations; application code authoritatively assigns real provenance
    source: Optional[str] = Field(default=None, description="Model-reported source (overwritten by application)")
    model_name: Optional[str] = Field(default=None, description="Model-reported model name (overwritten by application)")

class GeminiRecommendationBatchResponse(BaseModel):
    recommendations: List[GeminiRecommendationItem] = Field(
        default_factory=list,
        description="Collection of prioritized recommendations for the provided cloud instances"
    )
