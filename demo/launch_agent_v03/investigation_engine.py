"""Read-only, evidence-grounded investigation service for synthetic launch fixtures.

This module is a deterministic agent orchestration prototype: natural-language intent
routing into an ALLOWLIST of approved semantic queries and an evidence-aware decision
brief. It is NOT a general LLM, production auth layer, or causality engine.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from semantic_launch import run, synthetic_identity

AGENT_VERSION = "launch-investigation-v0.1"
ALLOWED_LAUNCHES = {"ZELDA_2026", "SWITCH2_2025"}


def _rows(root: Path, name: str) -> list[dict[str, str]]:
    with (root / name).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _intent(question: str) -> str:
    q = question.lower()
    if any(x in q for x in ("checkout", "guest", "authenticated", "login")):
        return "checkout"
    if any(x in q for x in ("new-to-franchise", "new to franchise", "new customer", "new-to-brand")):
        return "new_customer_progression"
    if any(x in q for x in ("product", "console", "controllers", "bundle", "item")):
        return "product"
    return "executive_launch"


def investigate(data_dir: str | Path, question: str, launch_id: str = "ZELDA_2026") -> dict[str, Any]:
    if launch_id not in ALLOWED_LAUNCHES:
        raise ValueError("Launch not in approved query catalog")
    root = Path(data_dir)
    summary = run(root, launch_id)
    intent = _intent(question)
    segment_rows = _rows(root, "customer_launch_segments.csv")
    membership = {x["customer_key"]: x["primary_segment"] for x in segment_rows if x["launch_id"] == launch_id}
    events = _rows(root, "ga4_events.csv")
    eligible_events = [e for e in events if e["launch_id"] == launch_id and synthetic_identity(e) in membership]
    by_segment_event: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for event in eligible_events:
        by_segment_event[membership[synthetic_identity(event)]][event["event_name"]].add(synthetic_identity(event))
    orders = [o for o in _rows(root, "orders.csv") if o["launch_id"] == launch_id and o["order_status"] == "completed"]
    customers_by_seg: dict[str, set[str]] = defaultdict(set)
    for key, seg in membership.items():
        customers_by_seg[seg].add(key)
    buyers_by_seg: dict[str, set[str]] = defaultdict(set)
    order_checkout: dict[str, Counter] = defaultdict(Counter)
    for o in orders:
        seg = membership.get(o["customer_key"])
        if seg:
            buyers_by_seg[seg].add(o["customer_key"])
            order_checkout[seg][o["checkout_type"]] += 1
    seg_rows = []
    for seg in sorted(customers_by_seg):
        ev = by_segment_event[seg]
        reached = len(ev["session_start"])
        buyers = len(buyers_by_seg[seg])
        seg_rows.append({
            "segment": seg,
            "reached_customers": reached,
            "pdp_view_customers": len(ev["view_item"]),
            "wishlist_customers": len(ev["add_to_wishlist"]),
            "cart_customers": len(ev["add_to_cart"]),
            "search_customers": len(ev["search"]),
            "purchasing_customers": buyers,
            "purchase_per_reached": round(buyers / reached, 5) if reached else None,
            "checkout_orders": dict(order_checkout[seg]),
            "segment_validation": "synthetic_scenario_label_unverified",
        })
    seg_by_name = {r["segment"]: r for r in seg_rows}
    target = seg_by_name.get("new_to_franchise") if launch_id == "ZELDA_2026" else None
    comparison = seg_by_name.get("existing_zelda_gamer") if target else None
    if target and comparison:
        gap_pp = round(100 * (target["purchase_per_reached"] - comparison["purchase_per_reached"]), 2)
        comparison_note = (
            f"New-to-franchise: {target['purchasing_customers']}/{target['reached_customers']} purchasing "
            f"({100*target['purchase_per_reached']:.1f}%); existing Zelda gamers: "
            f"{comparison['purchasing_customers']}/{comparison['reached_customers']} "
            f"({100*comparison['purchase_per_reached']:.1f}%). Difference: {gap_pp:+.2f} percentage points "
            "(descriptive; cohort definitions are scenario-assigned, not validated)."
        )
    else:
        comparison_note = "Segment-level observational comparisons available; no validated like-for-like control."
    missing = ["Verified customer relationship/ownership identity", "Campaign exposure and audience-quality joins",
               "Stock availability changes at event time", "Customer research or coded VOC for friction explanations",
               "Controlled experiment or causal comparison"]
    hypotheses = [
        {"name": "Product information or familiarity gap", "status": "hypothesis_only", "confidence": "not_estimable",
         "for": ["Lower observed purchase participation may motivate further discovery checks."],
         "against_or_unknown": ["No validated task-success, comprehension or VOC evidence."],
         "minimum_validation": "Compare search, PDP, wishlist and cart participation conditional on qualified exposure, then review relevant VOC."},
        {"name": "Acquisition mix or audience intent", "status": "hypothesis_only", "confidence": "not_estimable",
         "for": ["Customer cohorts have different illustrative purchase participation."],
         "against_or_unknown": ["No customer-grain marketing exposures or controlled source mix comparison."],
         "minimum_validation": "Join governed campaign-touch evidence and compare same-channel, same-product, similar-time cohorts."},
        {"name": "Checkout, availability or measurement friction", "status": "hypothesis_only", "confidence": "not_estimable",
         "for": ["Order checkout types exist; cart, event and order counts can be audited."],
         "against_or_unknown": ["No checkout attempt/failure, inventory history or customer complaints in current fixtures."],
         "minimum_validation": "Check inventory and checkout-step/error telemetry with eligible cart cohorts; verify event-to-order quality."},
    ]
    if intent == "checkout":
        hypotheses = [hypotheses[2], hypotheses[0], hypotheses[1]]
    result = {
        "agent_version": AGENT_VERSION, "mode": "synthetic_read_only", "executive_question": question,
        "intent": intent, "clarifying_questions_asked": 0, "max_questions": 5,
        "decision": "Investigate customer progression before changing campaign, product or checkout execution.",
        "semantic_contract": {"approved_query": "launch_segment_progression", "semantic_version": summary["semantic_version"],
                             "launch_id": launch_id, "grain": "distinct mapped synthetic customer per launch and milestone",
                             "customer_identity": "fixture-only pseudo-ID convention; not production identity resolution",
                             "segment_definition": "scenario-assigned, mutually exclusive, unverified",
                             "time_window": summary["evidence"]["observation"],
                             "primary_metric": "completed-order purchasing customers / reached customers",
                             "read_only": True, "causal_claims_permitted": False},
        "observed": {"launch": summary["metrics"], "segments": seg_rows, "comparison": comparison_note},
        "hypotheses": hypotheses,
        "small_list_tests": [
            {"type": "read_only_analysis", "priority": 1, "name": "Cohort milestone comparison",
             "required_evidence": "Cross-tab reached, PDP, search, wishlist, cart and purchased by segment × product × source, validating eligible denominators.",
             "primary_outcome": "Qualified progression to purchase", "guardrail": "Identity and tracking coverage", "approval": "Analytics methodology approval"},
            {"type": "conditional_experiment", "priority": 2, "name": "Clarity/personalization experiment (only if comprehension hypothesis supported)",
             "required_evidence": "Qualified audience, randomized exposure assignment, stable inventory and product mapping.",
             "primary_outcome": "Incremental qualified purchase rate", "guardrail": "Checkout errors, unsubscribes/experience complaints", "approval": "Business and Analytics required"},
        ],
        "missing_evidence": missing,
        "orchestration_health": {"status": "not_connected", "outbound_actions": [], "external_ids": [],
                                 "health_to_verify": ["campaign delivery", "consent/suppression", "inventory", "tracking completeness", "experiment integrity"]},
        "golden_insights": {"status": "rule_checks_only", "checks": {
            "uses_governed_semantics": True, "labels_synthetic_data": True,
            "separates_observation_from_hypothesis": True, "causal_claims_without_test": False,
            "customer_segment_validated": False, "unapproved_writes": False},
            "next_gate": "Analytics evidence/method review; independent evaluator not deployed"},
        "data_quality": summary["quality"],
        "source_provenance": summary["evidence"],
    }
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--launch-id", default="ZELDA_2026")
    args = p.parse_args()
    print(json.dumps(investigate(args.data_dir, args.question, args.launch_id), indent=2))


if __name__ == "__main__":
    main()