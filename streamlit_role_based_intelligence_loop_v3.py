import pandas as pd
import streamlit as st

st.set_page_config(page_title="Marketing Intelligence Loop V3", layout="wide")
st.title("Marketing Intelligence Loop V3")
st.caption("Shared evidence, different decisions: one AI + human learning loop for Marketing, Product, CRM, Executives, Performance, and Agency teams.")

ROLES = [
    "Executive",
    "CRM Leader",
    "Product Leader",
    "Integrated Marketing Leader",
    "Performance Marketing Leader",
    "Agency Partner",
]

# -----------------------------
# Shared evidence layer
# -----------------------------
JOURNEY = pd.DataFrame([
    ["Awareness", 105_000_000, 48, "Historical", "First-time visitors"],
    ["Interest", 52_000_000, 8, "Historical", "3+ page viewers"],
    ["Purchase", 4_100_000, 38, "Historical", "First purchasers"],
    ["Repeat", 1_600_000, 56, "Historical", "Second+ purchasers"],
    ["Advocacy", 893_000, None, "Historical", "3+ purchasers"],
], columns=["stage", "users", "continuation_rate", "evidence_age", "behavioral_definition"])

LEVERAGE = pd.DataFrame([
    ["Awareness -> Interest", 2, 5.6, "Historical scenario"],
    ["Interest -> Purchase", 2, 47.0, "Historical scenario"],
    ["Purchase -> Repeat", 2, 2.3, "Historical scenario"],
    ["Repeat -> Advocacy", 2, 2.6, "Historical scenario"],
], columns=["transition", "lift_pp", "modeled_revenue_m", "evidence_age"])

CHANNEL_SIGNALS = pd.DataFrame([
    ["Paid YouTube", "the system Featured Games", 52, "Share of weekly page-growth contribution", "Observed", "2026-08-09 to 2026-08-15"],
    ["Paid TikTok", "the system Featured Games", 43, "Share of weekly page-growth contribution", "Observed", "2026-08-09 to 2026-08-15"],
    ["Paid YouTube", "the system System PDP", 65, "Share of weekly page-growth contribution", "Observed", "2026-08-09 to 2026-08-15"],
    ["Paid TikTok", "the system Features", 96, "Share of weekly page-growth contribution", "Observed", "2026-08-09 to 2026-08-15"],
    ["Loyalty email", "Happy Birthday Exclusives", 88, "Share of weekly page-growth contribution", "Observed", "2026-08-09 to 2026-08-15"],
    ["Organic Search", "Oblivion Remastered PDP", 48, "Share of weekly page-growth contribution", "Observed", "2026-08-09 to 2026-08-15"],
], columns=["channel", "destination", "value", "metric", "evidence_state", "period"])

LANDING_SIGNALS = pd.DataFrame([
    ["Power up your play", 77.0, 2.1, "Learn More", "Hardware-shopping traffic; next step may be unclear", "Inferred"],
    ["Unwind with the system", 71.0, 5.5, "Buy Now", "Higher purchase intent, but CTA routed to sold-out bundle", "Inferred"],
], columns=["landing_experience", "bounce_rate_pct", "top_cta_ctr_pct", "top_cta", "interpretation", "evidence_state"])

RAILS = pd.DataFrame([
    ["Home", "Recently Viewed", 13.54, 20.9, 11.6, "Current working evidence"],
    ["Home", "Digital Best Sellers", 3.41, 13.5, 6.6, "Current working evidence"],
    ["Home", "Digital New Releases", 2.89, 11.4, 4.4, "Current working evidence"],
    ["Store Home", "New Releases", 3.19, 16.4, 10.2, "Current working evidence"],
    ["Store Home", "system Accessories", 1.94, 11.7, 6.4, "Current working evidence"],
    ["PDP", "DLC", 11.34, 26.9, 14.7, "Current working evidence"],
    ["PDP", "Recently Viewed", 10.34, 26.4, 11.2, "Current working evidence"],
    ["PDP", "More Like This", 9.64, 17.9, 6.8, "Current working evidence"],
    ["PDP", "Related Items to Explore", 6.30, 14.1, 7.8, "Current working evidence"],
    ["PDP", "Digital Best Sellers", 4.41, 15.8, 5.4, "Current working evidence"],
], columns=["page", "rail", "ctr_pct", "click_to_purchase_pct", "same_session_purchase_pct", "evidence_age"])

LEARNINGS = pd.DataFrame([
    ["Personalized cohort", "Interest -> Purchase", "29% vs 8% overall", "Observed association", "Needs causal validation"],
    ["Logged-in cohort", "Interest -> Purchase", "23% vs 8% overall", "Observed association", "Needs causal validation"],
    ["Deal-shopper experience", "Interest -> Purchase", "10% vs 8% baseline", "Observed association", "Needs causal validation"],
    ["PDP rail", "DLC", "26.9% click-to-purchase", "Current observation", "Candidate for deeper personalization test"],
    ["Home rail", "Recently Viewed", "20.9% click-to-purchase", "Current observation", "Strong continuity signal"],
], columns=["knowledge_area", "signal", "result", "evidence_state", "next_status"])

OWNERSHIP = pd.DataFrame([
    ["1. Business objective", "Jane / Business Lead", "Marketing leadership, Product, Sales/GTM", "Human owns the decision, customer context, constraints, and success criteria"],
    ["2. Trusted evidence layer", "Analytics Engineering / Data Engineering", "Jane, Marketing Ops, CRM owners", "Engineering owns durable pipelines; Jane co-owns business definitions, grain, reconciliation, and validation"],
    ["3. Signal detection", "AI Agent", "Jane", "AI monitors anomalies and patterns; signals remain observations until interpreted"],
    ["4. Customer + journey interpretation", "Jane", "Research, Marketing, Product, AI Agent", "Human judgment connects behavior to likely customer state, intent, and friction"],
    ["5. Diagnosis", "Jane + AI Agent", "Domain stakeholders", "AI broadens competing explanations; Jane applies business context and removes implausible diagnoses"],
    ["6. Hypothesis ranking", "Jane + AI Agent", "Data Science / functional experts", "AI increases hypothesis throughput; Jane owns evidence standards and inference boundaries"],
    ["7. Continuous exploration", "AI Agent", "Jane", "AI scales repetitive cuts across segment, channel, geo, device, campaign, and journey stage"],
    ["8. Experimentation + validation", "Jane / Analytics", "Data Science, Product, Marketing, Engineering", "Humans own causal claims, statistical rigor, instrumentation validity, and test design"],
    ["9. Recommendation + prioritization", "Jane", "Business leaders / decision owner", "Analytics converts evidence into a prioritized decision with confidence and trade-offs"],
    ["10. Activation", "Business / Functional Owner", "Jane, Product, Marketing, Engineering, Agency", "The accountable function owns execution; analytics supports the decision and learning plan"],
    ["11. Outcome measurement", "Jane / Analytics", "Data Engineering, business owner", "Analytics defines primary, leading, and guardrail measures tied to the original objective"],
    ["12. Learning + re-check", "Jane + AI Agent", "Broader analytics organization", "Validated learning is stored with context and re-tested as new evidence arrives"],
], columns=["loop_stage", "primary_owner", "key_collaborators", "ownership_boundary"])

ROLE_VIEW = {
    "Executive": {
        "question": "Where is the biggest credible growth opportunity, and what decision should leadership make next?",
        "focus": ["Economic leverage", "Journey bottlenecks", "Investment trade-offs", "Confidence / unknowns"],
        "default_signal": "Historical journey economics show Interest -> Purchase as the largest modeled +2pp revenue opportunity; current campaign evidence suggests upstream demand can be strong while downstream progression still breaks.",
        "recommendation": "Prioritize fixing the highest-value journey constraint before scaling acquisition; validate with current revenue and experiment evidence before committing investment.",
    },
    "CRM Leader": {
        "question": "Which customer state needs a different lifecycle treatment, and what should we test next?",
        "focus": ["Repeat / advocacy", "Identity and login", "Owned-channel signals", "Personalization"],
        "default_signal": "Historical personalized and logged-in cohorts show much stronger downstream continuation, while loyalty email has demonstrated strong traffic contribution to rewards/exclusives experiences.",
        "recommendation": "Use lifecycle state and known-customer context to test next-best content or product discovery before defaulting to higher message frequency or discounting.",
    },
    "Product Leader": {
        "question": "Where is the digital journey breaking, and which experience change is most likely to improve progression?",
        "focus": ["Page role", "Funnel leakage", "Recommendation rails", "Landing / checkout friction"],
        "default_signal": "Current PDP evidence shows contextual and behavioral rails outperform generic popularity; campaign landing pages also show clear downstream CTA friction despite strong traffic generation.",
        "recommendation": "Prioritize experience relevance and intent preservation: contextual rails on PDP, continuity on Home, and clearer next-step CTAs on campaign landings.",
    },
    "Integrated Marketing Leader": {
        "question": "Are channels working together across the customer journey, or are we losing intent between touchpoints?",
        "focus": ["Channel role", "Message-to-landing continuity", "Journey stage", "Cross-functional handoff"],
        "default_signal": "Paid YouTube/TikTok can generate material demand, but landing evidence shows that strong media traffic does not guarantee progression when the next step is unclear or unavailable.",
        "recommendation": "Measure campaigns end-to-end from media signal through landing progression and purchase intent; fix the weakest handoff before adding reach.",
    },
    "Performance Marketing Leader": {
        "question": "Which campaign or audience changes improve downstream value, not just clicks?",
        "focus": ["Traffic quality", "Post-click progression", "ROAS / conversion", "Audience / creative / geo cuts"],
        "default_signal": "Recent hardware campaigns drove large page-growth contributions, but one major landing experience had 77% bounce and only 2.1% CTR on its strongest internal CTA.",
        "recommendation": "Do not optimize on traffic contribution alone; diagnose post-click quality by audience, creative, device, landing page, and customer state before shifting spend.",
    },
    "Agency Partner": {
        "question": "What proactive client recommendation can we make before the next reporting cycle?",
        "focus": ["Cross-channel diagnosis", "Client story", "Evidence quality", "Experiment roadmap"],
        "default_signal": "The shared evidence shows a recurring pattern: media can create demand while owned experience suppresses progression, so platform performance alone can misstate business impact.",
        "recommendation": "Shift the client conversation from channel reporting to journey diagnosis, then propose the smallest test that distinguishes media-quality issues from landing/product friction.",
    },
}

role = st.sidebar.selectbox("View as", ROLES)
view = ROLE_VIEW[role]
st.sidebar.markdown("**Evidence states**")
st.sidebar.caption("Observed | Inferred | Unknown | Recommended | Validated / Rejected")
st.sidebar.markdown("**V3 principle**")
st.sidebar.caption("Same evidence layer. Different decision interface.")
st.sidebar.markdown("**Ownership principle**")
st.sidebar.caption("AI finds possibilities. Engineering creates trusted infrastructure. Analytics determines meaning. Business owners act.")

st.header(role)
st.write(view["question"])

with st.expander("Who owns what in the intelligence loop", expanded=True):
    st.dataframe(OWNERSHIP, use_container_width=True, hide_index=True)
    st.caption("Ownership is intentionally shared: no single actor owns the full loop. The handoff is part of the design, not a gap.")

# 1 Objective
st.subheader("1. Business objective")
objective = st.text_area("Decision to support", value=view["question"], height=70)
st.caption("Owner: Jane / Business Lead. Define the business decision, customer context, constraints, and what success means. AI may decompose the problem, but cannot invent the objective.")

# 2 Shared evidence
st.subheader("2. Shared trusted evidence layer")
t1, t2, t3, t4 = st.tabs(["Journey", "Campaign / channel", "Recommendation rails", "Learning library"])
with t1:
    st.dataframe(JOURNEY, use_container_width=True, hide_index=True)
    st.dataframe(LEVERAGE, use_container_width=True, hide_index=True)
    st.caption("Historical precedent: revalidate with current data before forecasting or causal claims.")
with t2:
    st.dataframe(CHANNEL_SIGNALS, use_container_width=True, hide_index=True)
    st.dataframe(LANDING_SIGNALS, use_container_width=True, hide_index=True)
with t3:
    st.dataframe(RAILS, use_container_width=True, hide_index=True)
    st.caption("Current working evidence; descriptive unless an experiment is available.")
with t4:
    st.dataframe(LEARNINGS, use_container_width=True, hide_index=True)
st.caption("Owner: Analytics Engineering / Data Engineering for durable pipelines; Jane / Analytics co-owns business definitions, grain, reconciliation, and validation. Single source of truth means one governed metric definition, not necessarily one source system.")

# 3 Signal monitoring
st.subheader("3. AI signal monitoring")
for item in view["focus"]:
    st.write(f"- {item}")
st.info(view["default_signal"])
st.caption("Owner: AI Agent, reviewed by Jane. Boundary: a signal is an observation. The agent cannot jump directly from movement to a recommendation.")

# 4 Journey interpretation
st.subheader("4. Customer + journey interpretation")
st.write("The agent maps signals to likely journey state, customer segment, and touchpoint role, then asks: what is the customer trying to do next, and what is blocking progression?")
journey_stage = st.selectbox("Likely journey stage", JOURNEY["stage"].tolist())
st.caption("Owner: Jane. Collaborators: Research, Marketing, Product, AI Agent. Human judgment challenges inferred journey state using VOC, research, segmentation, and business context.")

# 5 Diagnosis
st.subheader("5. Diagnosis")
diag_options = [
    "Audience / traffic quality",
    "Message or creative mismatch",
    "Landing-page / product experience friction",
    "Offer / price / availability",
    "Navigation / recommendation relevance",
    "Checkout / identity friction",
    "Measurement or data-quality issue",
]
selected_diag = st.multiselect("Candidate diagnostic areas", diag_options, default=diag_options[:3])
st.caption("Owner: Jane + AI Agent. AI should search for competing explanations, not protect its first hypothesis; Jane applies domain context and evidence standards.")

# 6 Hypothesis layer
st.subheader("6. Ranked hypotheses")
hypotheses = []
for i, h in enumerate(selected_diag[:5], 1):
    hypotheses.append([i, h, "Needs evidence", "Medium" if i <= 2 else "Low"])
st.dataframe(pd.DataFrame(hypotheses, columns=["rank", "hypothesis", "state", "confidence"]), use_container_width=True, hide_index=True)
st.caption("Owner: Jane + AI Agent. Collaborate with Data Science / functional experts when needed. Jane removes implausible hypotheses, adds missing context, and keeps inference separate from fact.")

# 7 Continuous testing
st.subheader("7. Continuous exploration + testing")
axes = st.multiselect(
    "AI can continuously test across",
    ["Journey stage", "Segment", "Channel", "Campaign", "Creative", "Geo", "Device", "Landing page", "Product", "New vs returning", "Login state"],
    default=["Journey stage", "Segment", "Channel", "Landing page"],
)
checks = max(1, len(axes)) * 24
c1, c2, c3 = st.columns(3)
c1.metric("Illustrative automated checks / day", checks)
c2.metric("Deep human validations / month", "2-5")
c3.metric("Evidence status", "Exploratory")
st.caption("Owner: AI Agent for exploration throughput; Jane prioritizes and reviews. AI's advantage is hypothesis throughput. Human advantage is context, statistical rigor, causal judgment, and accountability.")

# 8 Validation
st.subheader("8. Experimentation + validation")
validation = st.selectbox("Best validation path", [
    "A/B test",
    "Holdout / incrementality test",
    "Cohort or funnel analysis",
    "Regression / statistical model",
    "Instrumentation / data QA first",
])
st.write(f"Selected validation path: **{validation}**")
st.caption("Owner: Jane / Analytics. Collaborators: Data Science, Product, Marketing, Engineering. Automated exploration may surface patterns, but humans own causal claims, statistical rigor, instrumentation validity, and experiment design.")

# 9 Recommendation
st.subheader("9. Recommendation + prioritization")
st.warning(view["recommendation"])
col1, col2, col3 = st.columns(3)
col1.metric("Confidence", "Medium")
col2.metric("Action state", "Test before scale")
col3.metric("Decision owner", role)
st.caption("Owner: Jane for analytical recommendation and prioritization; the business decision owner remains accountable for the final decision.")

# 10 Activation
st.subheader("10. Activation")
action = st.radio("Human decision", ["Approve test", "Request more evidence", "Reject", "Escalate cross-functionally"], horizontal=True)
st.write(f"Decision: **{action}**")
st.caption("Owner: Business / Functional Owner. Collaborators: Jane, Product, Marketing, Engineering, Agency. Analytics supports the decision and learning plan; the accountable function owns execution.")

# 11 Outcome measurement
st.subheader("11. Outcome measurement")
outcomes = pd.DataFrame([
    ["Primary", "Revenue / conversion / retention / customer progression", "Must match original objective"],
    ["Leading", "Next-stage behavior", "Useful for faster learning"],
    ["Guardrail", "CX / margin / data quality / long-term retention", "Prevents local optimization"],
], columns=["metric_type", "example", "rule"])
st.dataframe(outcomes, use_container_width=True, hide_index=True)
st.caption("Owner: Jane / Analytics for the measurement framework; Data Engineering supports reliable instrumentation and the business owner remains accountable for the outcome.")

# 12 Learning loop
st.subheader("12. Learning + re-check")
learning_state = st.radio("What did the evidence show?", ["Not tested", "Validated", "Rejected", "Mixed / context dependent"], horizontal=True)
st.write(f"Learning state: **{learning_state}**")
st.caption("Owner: Jane + AI Agent. Validated findings are stored with segment, context, date, method, and confidence. The agent re-checks prior conclusions as new evidence arrives.")

st.divider()
st.subheader("Closed loop")
st.code("Objective -> Trusted Data -> Detect -> Interpret -> Diagnose -> Hypothesize -> Test -> Validate -> Recommend -> Act -> Measure -> Learn -> Detect again", language="text")
st.markdown("**Core evidence boundary:** Observed -> Inferred -> Unknown -> Recommended -> Validated / Rejected")
st.markdown("**Ownership loop:** Business -> Engineering -> AI -> Analyst -> Business -> Measure -> Learn")
st.success("V3 differentiator: the same evidence layer supports different role-specific decisions without creating six separate versions of truth. Ownership is explicit at every stage so AI acceleration does not blur human accountability.")