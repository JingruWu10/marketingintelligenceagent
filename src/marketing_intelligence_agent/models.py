from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class KPIObservation(BaseModel):
    metric: str
    current: float
    prior: float
    segment: str = "all"
    channel: Optional[str] = None

    @property
    def pct_change(self) -> float:
        if self.prior == 0:
            return 0.0
        return (self.current - self.prior) / self.prior


class BusinessContext(BaseModel):
    objective: str
    customer_segment: str = "all"
    journey_stage: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    label: Literal["observed", "inferred", "unknown", "recommended"]
    text: str


class Hypothesis(BaseModel):
    statement: str
    confidence: Literal["low", "medium", "high"]
    evidence_needed: List[str]


class Recommendation(BaseModel):
    action: str
    owner: str
    primary_kpi: str
    leading_indicator: Optional[str] = None
    guardrail: Optional[str] = None


class AnalysisOutput(BaseModel):
    what_changed: List[str]
    hypotheses: List[Hypothesis]
    where_in_journey: str
    what_to_check_next: List[str]
    recommendation: Recommendation
    evidence: List[EvidenceItem]


class AISynthesis(BaseModel):
    """Structured output from the LLM collaboration layer."""

    executive_summary: str
    observed: List[str]
    inferred: List[str]
    unknown: List[str]
    recommended: List[str]
    next_analysis: List[str]
    confidence: Literal["low", "medium", "high"]


class AIAnalysisOutput(BaseModel):
    """Deterministic analytics plus a separately auditable AI synthesis."""

    deterministic: AnalysisOutput
    ai_synthesis: AISynthesis
