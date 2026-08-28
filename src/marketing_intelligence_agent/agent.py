from __future__ import annotations

from typing import Iterable

from .models import (
    AnalysisOutput,
    BusinessContext,
    EvidenceItem,
    KPIObservation,
    Recommendation,
)
from .rules import detect_signals, generate_hypotheses, segment_spread


class MarketingIntelligenceAgent:
    """Decision-partner prototype.

    This class deliberately separates deterministic analytical guardrails from any LLM layer.
    An LLM can later be added for synthesis, query generation, and hypothesis expansion, while
    validation logic and metric definitions remain explicit and testable.
    """

    def analyze(self, context: BusinessContext, observations: Iterable[KPIObservation]) -> AnalysisOutput:
        rows = list(observations)
        signals = detect_signals(rows)
        signals.extend(segment_spread(rows))
        hypotheses = generate_hypotheses(rows)

        if context.journey_stage:
            journey = context.journey_stage
        else:
            journey = "Unknown - infer only after segmenting the observed behavior."

        next_checks = []
        for h in hypotheses[:3]:
            for item in h.evidence_needed:
                if item not in next_checks:
                    next_checks.append(item)

        recommendation = Recommendation(
            action=(
                "Validate the highest-confidence hypothesis with the smallest discriminating analysis "
                "before changing campaign or product strategy."
            ),
            owner="Analytics + relevant business owner",
            primary_kpi="next-stage progression rate",
            leading_indicator="validated leading behavior",
            guardrail="customer experience / data-quality guardrail",
        )

        evidence = [EvidenceItem(label="observed", text=s) for s in signals]
        evidence.extend(
            EvidenceItem(label="inferred", text=h.statement) for h in hypotheses
        )
        evidence.append(
            EvidenceItem(
                label="recommended",
                text="Do not jump from aggregate KPI change directly to a campaign recommendation.",
            )
        )

        return AnalysisOutput(
            what_changed=signals or ["No material signal crossed the configured threshold."],
            hypotheses=hypotheses,
            where_in_journey=journey,
            what_to_check_next=next_checks,
            recommendation=recommendation,
            evidence=evidence,
        )
