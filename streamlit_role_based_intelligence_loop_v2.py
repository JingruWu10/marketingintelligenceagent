import pandas as pd
import streamlit as st

st.set_page_config(page_title="Marketing Intelligence Loop v2", layout="wide")
st.title("Marketing Intelligence Loop v2")
st.caption("A role-based AI + human decision system with shared evidence, hypotheses, tests, actions, and learning.")

ROLES = [
    "CRM Leader",
    "Executive",
    "Product Leader",
    "Integrated Marketing Leader",
    "Performance Marketing Leader",
    "Agency Partner",
]

ROLE_CONFIG = {
    "CRM Leader": {
        "focus": "Lifecycle, retention, reactivation, personalization, and revenue per customer",
        "kpis": [("30-day repeat rate", 22.4, 20.1, "%"), ("Email conversion", 4.8, 5.5, "%"), ("Reactivation rate", 8.2, 7.3, "%"), ("Revenue / customer", 71.0, 66.0, "$")],
        "signal": "Returning-customer purchase rate is improving overall, but the 30–60 day inactive segment is weakening after email engagement.",
        "context": "The issue is concentrated in previously active customers who still open email but do not progress to the next purchase.",
        "hypotheses": ["Offer/message is not relevant to current customer state", "Post-purchase follow-up is too slow", "Customers need product discovery rather than a discount"],
        "test": "Test personalized next-best-product content vs. generic promotional email for the 30–60 day inactive cohort.",
        "recommendation": "Prioritize a relevance test before increasing promotional frequency.",
        "owner": "CRM + Analytics",
    },
    "Executive": {
        "focus": "Growth, investment allocation, customer economics, and strategic trade-offs",
        "kpis": [("Revenue growth", 12.0, 9.0, "%"), ("Conversion", 3.9, 4.2, "%"), ("Retention", 61.0, 57.0, "%"), ("Marketing ROI", 3.4, 3.1, "x")],
        "signal": "Revenue growth is ahead of prior period, but conversion is softening while retention improves.",
        "context": "The business may be getting more value from existing customers while acquisition-to-purchase efficiency weakens.",
        "hypotheses": ["Growth is increasingly retention-led", "Acquisition mix shifted toward lower-intent traffic", "Landing or checkout friction is suppressing new-customer conversion"],
        "test": "Decompose revenue growth into acquisition, conversion, repeat purchase, and customer value; validate the binding constraint before reallocating investment.",
        "recommendation": "Do not chase more traffic until the acquisition-to-purchase leak is quantified.",
        "owner": "Marketing Leadership + Analytics",
    },
    "Product Leader": {
        "focus": "Journey friction, feature adoption, product discovery, and conversion progression",
        "kpis": [("PDP progression", 41.0, 45.0, "%"), ("Add-to-cart", 18.0, 16.0, "%"), ("Checkout completion", 54.0, 51.0, "%"), ("Return visits", 36.0, 31.0, "%")],
        "signal": "Add-to-cart and checkout completion improved, but PDP-to-next-step progression declined.",
        "context": "High-intent customers convert once they act, but more visitors are failing to find the next relevant product/action.",
        "hypotheses": ["Recommendation content is mismatched to customer intent", "Page is serving both browsers and direct purchasers", "Discovery modules are poorly prioritized by segment"],
        "test": "Rank recommendation rails by segment and journey state, then test personalized rail order on PDP.",
        "recommendation": "Improve relevance before redesigning the entire PDP.",
        "owner": "Product + Analytics + Merchandising",
    },
    "Integrated Marketing Leader": {
        "focus": "Cross-channel journey, awareness-to-purchase progression, message consistency, and landing experience",
        "kpis": [("Reach", 118.0, 104.0, "M"), ("Consideration", 34.0, 30.0, "%"), ("Landing progression", 47.0, 52.0, "%"), ("Purchase intent", 19.0, 17.0, "%")],
        "signal": "Awareness and consideration are rising, but landing progression has weakened.",
        "context": "Media appears to create interest, but the owned experience may not preserve the promise or intent generated upstream.",
        "hypotheses": ["Landing message does not match campaign intent", "Wrong-region or wrong-product landing paths create friction", "Creative is attracting a broader audience than the page supports"],
        "test": "Connect campaign intent/creative theme to landing-page progression by audience and region.",
        "recommendation": "Fix the media-to-landing handoff before adding more reach.",
        "owner": "Integrated Marketing + Web/Product",
    },
    "Performance Marketing Leader": {
        "focus": "Spend efficiency, ROAS, audience quality, creative, and downstream conversion",
        "kpis": [("ROAS", 4.2, 4.6, "x"), ("CTR", 3.8, 3.4, "%"), ("CPC", 1.72, 1.81, "$"), ("Post-click CVR", 5.1, 6.0, "%")],
        "signal": "CTR improved and CPC fell, but ROAS and post-click conversion declined.",
        "context": "The campaign is buying engagement more efficiently, but that engagement is less likely to become revenue.",
        "hypotheses": ["Audience expansion reduced intent quality", "Creative improved clicks but over-promised", "Landing or product mix changed"],
        "test": "Segment post-click conversion by audience, creative, landing page, device, and customer status before changing bids.",
        "recommendation": "Optimize for downstream quality, not CTR alone.",
        "owner": "Performance Marketing + Analytics",
    },
    "Agency Partner": {
        "focus": "Client performance, proactive diagnosis, experimentation, and evidence-backed recommendations",
        "kpis": [("Client revenue", 108.0, 100.0, "index"), ("Media spend", 112.0, 100.0, "index"), ("Conversion", 3.5, 3.8, "%"), ("Incrementality tests", 7.0, 3.0, "#")],
        "signal": "Revenue is up, but spend increased faster and conversion weakened.",
        "context": "The client may still be growing, but efficiency and incrementality need validation before scaling.",
        "hypotheses": ["Higher spend is reaching diminishing-return audiences", "Channel mix changed", "Revenue growth is driven by demand that would have occurred without the campaign"],
        "test": "Prioritize an incrementality test and decompose performance by audience/channel/market before recommending more spend.",
        "recommendation": "Move the client conversation from reporting growth to proving incremental growth.",
        "owner": "Agency Strategy + Client + Analytics",
    },
}

role = st.sidebar.selectbox("Choose your role", ROLES)
mode = st.sidebar.radio("Data mode", ["Demo data", "Upload KPI CSV"])

cfg = ROLE_CONFIG[role]

if mode == "Upload KPI CSV":
    uploaded = st.sidebar.file_uploader("Upload KPI CSV", type=["csv"])
    st.sidebar.caption("Optional columns: metric, current, prior, segment, channel, period")
else:
    uploaded = None

st.header(role)
st.write(cfg["focus"])

# Objective layer
st.subheader("1. Business objective")
objective = st.text_area("What decision are we trying to make?", value=cfg["test"], height=80)

# Data layer
st.subheader("2. Trusted data foundation")
if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.dataframe(df.head(50), use_container_width=True)
else:
    demo_df = pd.DataFrame(cfg["kpis"], columns=["metric", "current", "prior", "unit"])
    st.dataframe(demo_df, use_container_width=True, hide_index=True)

st.caption("Jane / human check: Are the metric definitions, time windows, segment logic, and sources trustworthy? Unknown data stays unknown.")

# Signal cards
st.subheader("3. Signal monitoring")
cols = st.columns(4)
for i, (name, current, prior, unit) in enumerate(cfg["kpis"]):
    delta = current - prior
    if unit == "$":
        value = f"${current:,.2f}"
        delta_text = f"${delta:+,.2f}"
    elif unit in ["%", "x", "M"]:
        value = f"{current:g}{unit}"
        delta_text = f"{delta:+.1f}{unit}"
    elif unit == "#":
        value = f"{current:.0f}"
        delta_text = f"{delta:+.0f}"
    else:
        value = f"{current:g}"
        delta_text = f"{delta:+.1f}"
    cols[i].metric(name, value, delta_text)

st.markdown("**Observed signal**")
st.info(cfg["signal"])

# Journey + diagnosis
left, right = st.columns(2)
with left:
    st.subheader("4. Journey interpretation")
    st.write(cfg["context"])
    st.caption("Boundary: journey state may be inferred, but uncertainty must remain visible.")
with right:
    st.subheader("5. Diagnosis")
    st.write("The agent does not jump directly from KPI movement to an action. It asks what changed, where, for whom, and what could explain it.")

# Hypotheses
st.subheader("6. Competing hypotheses")
hyp_df = pd.DataFrame({
    "rank": [1, 2, 3],
    "hypothesis": cfg["hypotheses"],
    "status": ["Needs validation", "Needs validation", "Needs validation"],
    "confidence": ["Medium", "Medium", "Low"],
})
st.dataframe(hyp_df, use_container_width=True, hide_index=True)
st.caption("Jane / human check: reject implausible explanations, add missing business context, and keep hypotheses separate from facts.")

# Continuous testing
st.subheader("7. Continuous exploration & lightweight testing")
checks = st.multiselect(
    "What should the AI continuously slice/test?",
    ["Segment", "Channel", "Geo", "Campaign", "Creative", "Landing page", "Product", "Device", "Journey stage", "New vs returning"],
    default=["Segment", "Channel", "Journey stage"],
)
throughput = len(checks) * 24 if checks else 0
c1, c2 = st.columns(2)
c1.metric("Illustrative AI checks / day", throughput)
c2.metric("Deep human validations / month", "2–5")
st.caption("Scale advantage: AI expands hypothesis throughput; humans focus on evidence quality, causality, trade-offs, and accountability.")

# Validation
st.subheader("8. Experimentation & validation")
st.success(cfg["test"])
st.caption("Boundary: automated exploration can suggest patterns; humans own experiment validity and causal claims.")

# Recommendation card
st.subheader("9. Recommendation & prioritization")
rec1, rec2, rec3 = st.columns(3)
rec1.metric("Confidence", "Medium")
rec2.metric("Decision status", "Test before scale")
rec3.metric("Owner", cfg["owner"])
st.warning(cfg["recommendation"])

# Activation
st.subheader("10. Activation")
action = st.selectbox("Human decision", ["Approve test", "Request more evidence", "Reject recommendation", "Escalate to cross-functional team"])
st.write(f"Selected: **{action}**")

# Outcome
st.subheader("11. Outcome measurement")
outcome_df = pd.DataFrame({
    "evidence type": ["Primary outcome", "Leading indicator", "Guardrail"],
    "example": ["Conversion / revenue / retention", "Next-stage progression", "Customer experience / margin / data quality"],
    "status": ["Monitor", "Monitor", "Monitor"],
})
st.dataframe(outcome_df, use_container_width=True, hide_index=True)

# Learning
st.subheader("12. Learning & re-check loop")
learning_status = st.radio("After measurement, what happened?", ["Not tested yet", "Validated", "Rejected", "Mixed / context-dependent"], horizontal=True)
st.write(f"Learning state: **{learning_status}**")
st.caption("Validated learnings are stored with segment, context, date, evidence, and confidence. The agent re-checks them as new data arrives.")

st.divider()
st.subheader("The loop")
st.code(
    "Objective -> Trusted Data -> Detect -> Interpret -> Diagnose -> Hypothesize -> Test -> Validate -> Recommend -> Act -> Measure -> Learn -> Detect again",
    language="text",
)
st.markdown("**Evidence boundary:** Observed -> Inferred -> Unknown -> Recommended -> Validated / Rejected")
