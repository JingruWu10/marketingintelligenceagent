from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List

from .models import KPIObservation, Hypothesis


def detect_signals(observations: Iterable[KPIObservation], threshold: float = 0.10) -> List[str]:
    signals = []
    for obs in observations:
        change = obs.pct_change
        if abs(change) >= threshold:
            direction = "increased" if change > 0 else "decreased"
            signals.append(
                f"{obs.metric} {direction} {abs(change):.1%} for segment={obs.segment}"
            )
    return signals


def segment_spread(observations: Iterable[KPIObservation]) -> List[str]:
    by_metric = defaultdict(list)
    for obs in observations:
        by_metric[obs.metric].append(obs)

    findings = []
    for metric, rows in by_metric.items():
        if len(rows) < 2:
            continue
        changes = [r.pct_change for r in rows]
        if max(changes) - min(changes) >= 0.15:
            findings.append(
                f"{metric} varies materially by segment; aggregate performance may hide different customer states."
            )
    return findings


def generate_hypotheses(observations: Iterable[KPIObservation]) -> List[Hypothesis]:
    rows = list(observations)
    hypotheses: List[Hypothesis] = []

    traffic = [r for r in rows if r.metric.lower() in {"sessions", "traffic", "visits"}]
    conversion = [r for r in rows if "conversion" in r.metric.lower() or "purchase" in r.metric.lower()]
    engagement = [r for r in rows if "engagement" in r.metric.lower() or "pdp" in r.metric.lower()]

    if traffic and conversion:
        traffic_change = sum(r.pct_change for r in traffic) / len(traffic)
        conv_change = sum(r.pct_change for r in conversion) / len(conversion)
        if abs(traffic_change) < 0.05 and conv_change < -0.10:
            hypotheses.append(
                Hypothesis(
                    statement="The primary issue is likely funnel progression rather than demand volume.",
                    confidence="high",
                    evidence_needed=["step-level funnel conversion", "segment mix", "experience/error telemetry"],
                )
            )

    if engagement and conversion:
        eng_change = sum(r.pct_change for r in engagement) / len(engagement)
        conv_change = sum(r.pct_change for r in conversion) / len(conversion)
        if eng_change > 0.10 and conv_change <= 0:
            hypotheses.append(
                Hypothesis(
                    statement="Interest may be increasing without successful progression to purchase.",
                    confidence="medium",
                    evidence_needed=["add-to-cart progression", "checkout friction", "inventory/price context"],
                )
            )

    if not hypotheses:
        hypotheses.append(
            Hypothesis(
                statement="The aggregate signal is insufficient for diagnosis; segment and journey decomposition should come first.",
                confidence="medium",
                evidence_needed=["customer segment", "journey stage", "channel", "downstream behavior"],
            )
        )
    return hypotheses
