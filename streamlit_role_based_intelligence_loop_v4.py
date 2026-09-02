from __future__ import annotations

import json
import os
import re
from typing import List, Literal

import pandas as pd
import streamlit as st
from openai import OpenAI
from pydantic import BaseModel, Field

st.set_page_config(page_title="Marketing Intelligence Loop V4", layout="wide")
st.title("Marketing Intelligence Loop V4")
st.caption("Human objective -> governed evidence -> AI monitoring -> exceptions -> prioritization -> diagnosis -> human validation -> decision -> activation -> outcome monitoring -> learning")

ROLES = [
    "Executive",
    "CRM Leader",
    "Product Leader",
    "Integrated Marketing Leader",
    "Performance Marketing Leader",
    "Agency Partner",
    "Analyst / Admin",
]

ROLE_QUESTIONS = {
    "Executive": "Which exceptions deserve leadership attention, what is the likely business impact, and what decision should leadership make next?",
    "CRM Leader": "Which customer-state exceptions need a different lifecycle treatment, and what should we validate next?",
    "Product Leader": "Which journey exceptions indicate meaningful experience friction, and which change should we validate?",
    "Integrated Marketing Leader": "Which cross-channel exceptions suggest customer intent is being lost, and where is the weakest handoff?",
    "Performance Marketing Leader": "Which campaign or audience exceptions materially affect downstream value, not just clicks?",
    "Agency Partner": "Which exceptions deserve proactive client attention, and what should be validated before scaling?",
    "Analyst / Admin": "What changed, why might it have changed, what evidence is missing, and what should we validate next?",
}

ROLE_VISIBILITY = {
    "Executive": {
        "evidence_sections": [],
        "show_packet": False,
        "show_observed": True,
        "show_inferred": False,
        "show_unknown": False,
        "show_hypotheses": False,
        "show_validation": False,
        "show_decision": True,
        "show_monitoring": True,
        "view_note": "Executive view: prioritized exception, business impact, decision, and outcome monitoring. Technical evidence and diagnostic detail stay underneath.",
    },
    "CRM Leader": {
        "evidence_sections": ["Journey", "Prior learning"],
        "show_packet": False,
        "show_observed": True,
        "show_inferred": True,
        "show_unknown": True,
        "show_hypotheses": True,
        "show_validation": True,
        "show_decision": True,
        "show_monitoring": True,
        "view_note": "CRM view: customer state, lifecycle exception, next-best action, validation, and outcome.",
    },
    "Product Leader": {
        "evidence_sections": ["Journey", "Landing", "Recommendation rails", "Prior learning"],
        "show_packet": False,
        "show_observed": True,
        "show_inferred": True,
        "show_unknown": True,
        "show_hypotheses": True,
        "show_validation": True,
        "show_decision": True,
        "show_monitoring": True,
        "view_note": "Product view: journey friction, behavioral evidence, competing explanations, product test, and guardrails.",
    },
    "Integrated Marketing Leader": {
        "evidence_sections": ["Journey", "Campaign / channel", "Landing", "Prior learning"],
        "show_packet": False,
        "show_observed": True,
        "show_inferred": True,
        "show_unknown": True,
        "show_hypotheses": True,
        "show_validation": True,
        "show_decision": True,
        "show_monitoring": True,
        "view_note": "Integrated Marketing view: cross-channel handoffs, customer intent, landing experience, activation, and measurement.",
    },
    "Performance Marketing Leader": {
        "evidence_sections": ["Campaign / channel", "Landing", "Prior learning"],
        "show_packet": False,
        "show_observed": True,
        "show_inferred": True,
        "show_unknown": True,
        "show_hypotheses": True,
        "show_validation": True,
        "show_decision": True,
        "show_monitoring": True,
        "view_note": "Performance view: campaign/audience exceptions, downstream value, landing diagnosis, incremental validation, and ROI outcome.",
    },
    "Agency Partner": {
        "evidence_sections": [],
        "show_packet": False,
        "show_observed": True,
        "show_inferred": True,
        "show_unknown": False,
        "show_hypotheses": False,
        "show_validation": True,
        "show_decision": True,
        "show_monitoring": True,
        "view_note": "Agency view: client-ready signal, evidence-backed recommendation, validation plan, and measurement. Internal technical detail and decision history remain hidden.",
    },
    "Analyst / Admin": {
        "evidence_sections": ["Journey", "Campaign / channel", "Landing", "Recommendation rails", "Prior learning"],
        "show_packet": True,
        "show_observed": True,
        "show_inferred": True,
        "show_unknown": True,
        "show_hypotheses": True,
        "show_validation": True,
        "show_decision": True,
        "show_monitoring": True,
        "view_note": "Analyst/Admin view: full evidence, hypotheses, validation, governance, decision, and learning loop.",
    },
}

# Public/shareable demo rule: keep source-company and branded platform/product references generic.
MASK_RULES = [
    (r"\bthe company\b", "the site"),
    (r"\bthe system\s*2\b", "page"),
    (r"\bthe system\b", "page"),
    (r"\bsystem\b", "page"),
]


def mask_text(value):
    if value is None:
        return value
    text = str(value)
    for pattern, replacement in MASK_RULES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def mask_obj(value):
    if isinstance(value, dict):
        return {k: mask_obj(v) for k, v in value.items()}
    if isinstance(value, list):
        return [mask_obj(v) for v in value]
    if isinstance(value, str):
        return mask_text(value)
    return value


class RankedHypothesis(BaseModel):
    hypothesis: str
    confidence: Literal["low", "medium", "high"]
    evidence_for: List[str] = Field(default_factory=list)
    evidence_needed: List[str] = Field(default_factory=list)


class DecisionSynthesis(BaseModel):
    executive_summary: str
    observed: List[str]
    inferred: List[str]
    unknown: List[str]
    ranked_hypotheses: List[RankedHypothesis]
    next_analyses: List[str]
    recommended_test: str
    recommendation: str
    primary_kpi: str
    leading_indicator: str
    guardrail: str
    confidence: Literal["low", "medium", "high"]


JOURNEY = [
    {"stage": "Awareness", "users": 105000000, "continuation_rate_pct": 48, "definition": "first-time visitors", "state": "historical"},
    {"stage": "Interest", "users": 52000000, "continuation_rate_pct": 8, "definition": "3+ page viewers", "state": "historical"},
    {"stage": "Purchase", "users": 4100000, "continuation_rate_pct": 38, "definition": "first purchasers", "state": "historical"},
    {"stage": "Repeat", "users": 1600000, "continuation_rate_pct": 56, "definition": "second+ purchasers", "state": "historical"},
    {"stage": "Advocacy", "users": 893000, "continuation_rate_pct": None, "definition": "3+ purchasers", "state": "historical"},
]

LEVERAGE = [
    {"transition": "Awareness -> Interest", "plus_2pp_revenue_m": 5.6, "state": "historical scenario"},
    {"transition": "Interest -> Purchase", "plus_2pp_revenue_m": 47.0, "state": "historical scenario"},
    {"transition": "Purchase -> Repeat", "plus_2pp_revenue_m": 2.3, "state": "historical scenario"},
    {"transition": "Repeat -> Advocacy", "plus_2pp_revenue_m": 2.6, "state": "historical scenario"},
]

CAMPAIGN = [
    {"channel": "Paid YouTube", "destination": "Featured Games Page", "growth_contribution_pct": 52, "state": "observed"},
    {"channel": "Paid TikTok", "destination": "Featured Games Page", "growth_contribution_pct": 43, "state": "observed"},
    {"channel": "Paid YouTube", "destination": "Hardware Product Page", "growth_contribution_pct": 65, "state": "observed"},
    {"channel": "Paid TikTok", "destination": "Product Features Page", "growth_contribution_pct": 96, "state": "observed"},
    {"channel": "Loyalty email", "destination": "Rewards / Exclusives Page", "growth_contribution_pct": 88, "state": "observed"},
]

LANDING = [
    {"experience": "Hardware Campaign Landing Page A", "bounce_rate_pct": 77.0, "top_cta_ctr_pct": 2.1, "top_cta": "Learn More", "state": "observed"},
    {"experience": "Hardware Campaign Landing Page B", "bounce_rate_pct": 71.0, "top_cta_ctr_pct": 5.5, "top_cta": "Buy Now", "destination_issue": "sold-out bundle", "state": "observed"},
]

RAILS = [
    {"page": "Home", "rail": "Recently Viewed", "ctr_pct": 13.54, "click_to_purchase_pct": 20.9, "same_session_purchase_pct": 11.6, "state": "observed"},
    {"page": "Home", "rail": "Digital Best Sellers", "ctr_pct": 3.41, "click_to_purchase_pct": 13.5, "same_session_purchase_pct": 6.6, "state": "observed"},
    {"page": "Store Home", "rail": "New Releases", "ctr_pct": 3.19, "click_to_purchase_pct": 16.4, "same_session_purchase_pct": 10.2, "state": "observed"},
    {"page": "PDP", "rail": "DLC", "ctr_pct": 11.34, "click_to_purchase_pct": 26.9, "same_session_purchase_pct": 14.7, "state": "observed"},
    {"page": "PDP", "rail": "Recently Viewed", "ctr_pct": 10.34, "click_to_purchase_pct": 26.4, "same_session_purchase_pct": 11.2, "state": "observed"},
    {"page": "PDP", "rail": "More Like This", "ctr_pct": 9.64, "click_to_purchase_pct": 17.9, "same_session_purchase_pct": 6.8, "state": "observed"},
]

PRIOR_LEARNINGS = [
    {"finding": "Personalized cohort Interest -> Purchase = 29% vs 8% overall", "state": "observational; causal validation needed"},
    {"finding": "Logged-in cohort Interest -> Purchase = 23% vs 8% overall", "state": "observational; causal validation needed"},
    {"finding": "PDP contextual/behavioral rails outperform generic popularity downstream", "state": "current descriptive evidence"},
]

SYSTEM_PROMPT = """You are a marketing intelligence decision-support collaborator operating over a governed evidence packet.

Operating philosophy:
Human defines objective -> governed evidence -> AI continuously monitors -> exception detection -> prioritization -> AI diagnosis/hypotheses -> human causal validation -> decision -> activation -> automated outcome monitoring -> learning.

Rules:
1. Never invent facts, metrics, research, experiment results, or causality.
2. Treat deterministic governed evidence as the evidence boundary. Do not recalculate or silently change supplied metrics.
3. Keep OBSERVED, INFERRED, UNKNOWN, and RECOMMENDED separate.
4. Historical scenarios are precedent, not current forecasts.
5. Descriptive/observational differences are not causal lift.
6. Do not make humans manually monitor every launch, campaign, segment, or market. Detect and prioritize the exceptions most deserving of human attention.
7. Prioritize exceptions by business impact, customer impact, confidence, urgency, and actionability.
8. Diagnose before recommending. Generate competing hypotheses rather than one confident story.
9. Segment and journey context matter; channels are roles in a customer journey, not isolated silos.
10. Recommend the smallest next analysis or experiment that could change the decision.
11. AI owns scalable monitoring, exception detection, prioritization, exploration, and hypothesis throughput. Humans own objectives, statistical validity, causal claims, customer/brand trade-offs, and final decisions.
12. After activation, specify the primary outcome, leading indicator, guardrail, and monitoring window so outcomes can be checked automatically and fed back into learning.
13. The underlying intelligence loop can be richer than the stakeholder-facing view. Tailor presentation depth to the role while preserving the same governed reasoning underneath.
14. Protect customer trust and do not infer sensitive traits.
15. Preserve anonymization. Never name the source brand, company, console, platform, or product. Refer to the source generically as the site or page.
Return only the requested structured schema."""


def evidence_packet(role: str, objective: str, stage: str, human_context: str, feedback: list[dict]) -> dict:
    packet = {
        "role": role,
        "role_default_question": ROLE_QUESTIONS[role],
        "role_visibility": ROLE_VISIBILITY[role]["view_note"],
        "objective": objective,
        "selected_journey_stage": stage,
        "human_context": human_context or "No additional context supplied.",
        "operating_philosophy": "Human objective -> governed evidence -> AI monitoring -> exception detection -> prioritization -> AI diagnosis/hypotheses -> human causal validation -> decision -> activation -> automated outcome monitoring -> learning",
        "evidence": {
            "journey_historical": JOURNEY,
            "historical_leverage_scenarios": LEVERAGE,
            "campaign_channel_observations": CAMPAIGN,
            "landing_observations": LANDING,
            "recommendation_rail_observations": RAILS,
            "prior_learnings": PRIOR_LEARNINGS,
        },
        "human_feedback_from_this_session": feedback,
        "evidence_boundary": ["observed", "inferred", "unknown", "recommended", "validated", "rejected"],
    }
    return mask_obj(packet)


def run_ai(packet: dict, api_key: str, model: str) -> DecisionSynthesis:
    client = OpenAI(api_key=api_key)
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Identify the highest-priority exception in this governed evidence packet, diagnose competing explanations, and recommend the smallest validation that could change the decision. Tailor the visible synthesis depth to the selected stakeholder role without weakening the underlying evidence discipline.\n\n" + json.dumps(packet, indent=2)},
        ],
        text_format=DecisionSynthesis,
    )
    if response.output_parsed is None:
        raise RuntimeError("OpenAI returned no structured synthesis.")
    return response.output_parsed


if "feedback" not in st.session_state:
    st.session_state.feedback = []
if "analysis" not in st.session_state:
    st.session_state.analysis = None

role = st.sidebar.selectbox("View as", ROLES)
visibility = ROLE_VISIBILITY[role]
model = st.sidebar.text_input("OpenAI model", value=os.getenv("OPENAI_MODEL", "gpt-5.6"))
api_key = st.sidebar.text_input("OpenAI API key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
st.sidebar.caption("For deployment, use a secret/environment variable rather than committing an API key.")
st.sidebar.markdown("**Role-based decision surface**")
st.sidebar.caption(visibility["view_note"])
st.sidebar.markdown("**Operating model**")
st.sidebar.caption("AI monitors broadly; humans focus on prioritized exceptions and causal decisions.")
st.sidebar.markdown("**Evidence boundary**")
st.sidebar.caption("Observed -> Inferred -> Unknown -> Recommended -> Validated / Rejected")
st.sidebar.markdown("**Anonymization**")
st.sidebar.caption("Source brand/company/platform/product references are generalized to site/page in shareable output.")

st.header(role)
st.caption(visibility["view_note"])
objective = st.text_area("Human-defined business objective", value=ROLE_QUESTIONS[role], height=80)
stage = st.selectbox("Journey stage", [x["stage"] for x in JOURNEY])
human_context = st.text_area("Human context", placeholder="Add known campaign context, customer research, business constraints, recent changes, or reasons an apparent exception may be misleading.", height=100)

section_data = {
    "Journey": lambda: (
        st.dataframe(pd.DataFrame(JOURNEY), use_container_width=True, hide_index=True),
        st.dataframe(pd.DataFrame(LEVERAGE), use_container_width=True, hide_index=True),
    ),
    "Campaign / channel": lambda: st.dataframe(pd.DataFrame(CAMPAIGN), use_container_width=True, hide_index=True),
    "Landing": lambda: st.dataframe(pd.DataFrame(LANDING), use_container_width=True, hide_index=True),
    "Recommendation rails": lambda: st.dataframe(pd.DataFrame(RAILS), use_container_width=True, hide_index=True),
    "Prior learning": lambda: st.dataframe(pd.DataFrame(PRIOR_LEARNINGS), use_container_width=True, hide_index=True),
}

if visibility["evidence_sections"]:
    st.subheader("Governed evidence relevant to this role")
    visible_sections = visibility["evidence_sections"]
    tabs = st.tabs(visible_sections)
    for tab, section_name in zip(tabs, visible_sections):
        with tab:
            section_data[section_name]()
else:
    st.info("The governed evidence layer is running underneath this view. Raw evidence tables are intentionally hidden for this role so attention stays on the decision surface.")

packet = evidence_packet(role, objective, stage, human_context, st.session_state.feedback)
if visibility["show_packet"]:
    with st.expander("Inspect exact anonymized evidence packet sent to AI"):
        st.json(packet)

if st.button("Run exception intelligence loop", type="primary"):
    if not api_key:
        st.error("Add OPENAI_API_KEY as an environment variable/secret or enter it in the sidebar for this session.")
    else:
        try:
            with st.spinner("AI is monitoring the evidence, prioritizing exceptions, and diagnosing competing explanations..."):
                st.session_state.analysis = run_ai(packet, api_key, model)
        except Exception as exc:
            st.error(f"AI synthesis failed: {exc}")

analysis = st.session_state.analysis
if analysis:
    st.subheader("Prioritized exception")
    st.info(mask_text(analysis.executive_summary))

    visible_columns = []
    if visibility["show_observed"]:
        visible_columns.append(("OBSERVED", analysis.observed))
    if visibility["show_inferred"]:
        visible_columns.append(("INFERRED", analysis.inferred))
    if visibility["show_unknown"]:
        visible_columns.append(("UNKNOWN", analysis.unknown))

    if visible_columns:
        columns = st.columns(len(visible_columns))
        for column, (label, items) in zip(columns, visible_columns):
            with column:
                st.markdown(f"**{label}**")
                for x in items:
                    st.write(f"- {mask_text(x)}")

    if visibility["show_hypotheses"]:
        st.subheader("Diagnosis and competing hypotheses")
        rows = []
        for i, h in enumerate(analysis.ranked_hypotheses, 1):
            rows.append({
                "rank": i,
                "hypothesis": mask_text(h.hypothesis),
                "confidence": h.confidence,
                "evidence_for": " | ".join(mask_text(x) for x in h.evidence_for),
                "evidence_needed": " | ".join(mask_text(x) for x in h.evidence_needed),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if visibility["show_validation"]:
        st.subheader("Human causal validation")
        for x in analysis.next_analyses:
            st.write(f"- {mask_text(x)}")
        st.success(f"Recommended validation: {mask_text(analysis.recommended_test)}")
        st.caption("AI can monitor and screen many launch x segment x channel x page x journey combinations; human analysts own statistical validity and causal interpretation.")

    if visibility["show_decision"]:
        st.subheader("Decision and activation")
        st.warning(mask_text(analysis.recommendation))
        a, b, c = st.columns(3)
        a.metric("AI confidence", analysis.confidence.upper())
        b.metric("Primary KPI", mask_text(analysis.primary_kpi))
        c.metric("Leading indicator", mask_text(analysis.leading_indicator))
        st.write(f"**Guardrail:** {mask_text(analysis.guardrail)}")

        decision = st.radio("Human decision", ["Need more evidence", "Approve test", "Activate", "Challenge", "Reject"], horizontal=True)
        feedback_note = st.text_input("Why? Add context the AI should learn from in the next cycle.")
        if st.button("Save human feedback"):
            st.session_state.feedback.append(mask_obj({"role": role, "objective": objective, "decision": decision, "note": feedback_note}))
            st.success("Anonymized feedback added to this session's next evidence packet.")

    if visibility["show_monitoring"]:
        st.subheader("Automated outcome monitoring and learning")
        monitoring_window = st.text_input("Monitoring window", placeholder="e.g. 7 days, 4 weeks, or through launch + 14 days")
        outcome_state = st.selectbox("Outcome evidence", ["Not measured yet", "Validated", "Rejected", "Mixed / context dependent"])
        outcome_note = st.text_area("Outcome / experiment note", placeholder="Record actual result, segment, method, date, confidence, and important conditions.")
        if st.button("Add outcome to learning loop"):
            st.session_state.feedback.append(mask_obj({"role": role, "objective": objective, "decision": "Outcome: " + outcome_state, "monitoring_window": monitoring_window, "note": outcome_note}))
            st.success("Anonymized outcome added to session learning. Re-run the intelligence loop to let the next cycle see it.")

st.divider()
st.subheader("Staff-scale decision system")
st.code("Human Objective -> Governed Evidence -> AI Continuous Monitoring -> Exception Detection -> Prioritization -> AI Diagnosis/Hypotheses -> Human Causal Validation -> Decision -> Activation -> Automated Outcome Monitoring -> Learning", language="text")
st.caption("The underlying intelligence loop stays constant. Each role sees only the layers needed for its decision. At scale, analysts design the measurement and decision system rather than manually monitoring every launch.")
