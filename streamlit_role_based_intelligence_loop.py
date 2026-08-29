import streamlit as st
import pandas as pd

st.set_page_config(page_title="Marketing Intelligence Loop", layout="wide")
st.title("Marketing Intelligence Loop")
st.caption("One continuous AI + human learning system, tailored to the decision needs of each marketing role.")

ROLES = [
    "CRM Leader",
    "Executive",
    "Product",
    "Integrated Marketing",
    "Campaign / Performance Marketing",
    "Agency",
]

LAYERS = [
    {
        "step": 1,
        "name": "Business Objective",
        "agent": "Translate a broad goal into measurable questions, decision criteria, and missing context.",
        "jane": "Feed business goals, customer problems, journey stage, constraints, and the decision that needs to change.",
        "boundary": "AI cannot invent the objective, assume causality, or redefine success without human approval.",
        "views": {
            "CRM Leader": "Retention, reactivation, nurture, repeat purchase, lifecycle progression.",
            "Executive": "Growth target, revenue opportunity, investment priorities, strategic trade-offs.",
            "Product": "Customer friction, journey completion, feature adoption, conversion barriers.",
            "Integrated Marketing": "Campaign objective, audience, journey role, cross-channel coordination.",
            "Campaign / Performance Marketing": "Spend efficiency, acquisition target, conversion goal, channel role.",
            "Agency": "Client objective, success definition, business context, campaign mandate.",
        },
    },
    {
        "step": 2,
        "name": "Trusted Data Foundation",
        "agent": "Connect approved web, CRM, media, commerce, product, research, VOC, and external signals.",
        "jane": "Define trusted sources, IDs, KPI definitions, taxonomy, privacy rules, and source-of-truth logic.",
        "boundary": "Only governed, approved data can become evidence; unknown or missing data stays explicitly unknown.",
        "views": {
            "CRM Leader": "Customer profiles, CRM status, email behavior, lifecycle events, purchase history.",
            "Executive": "Unified business metrics, revenue, pipeline, retention, channel contribution.",
            "Product": "Behavioral events, feature usage, funnel progression, error/friction signals.",
            "Integrated Marketing": "Paid + owned + earned + CRM + web touchpoints in one customer journey view.",
            "Campaign / Performance Marketing": "Spend, impressions, clicks, conversions, attribution inputs, landing behavior.",
            "Agency": "Client campaign data, media platform data, web outcomes, agreed KPI definitions.",
        },
    },
    {
        "step": 3,
        "name": "Signal Monitoring",
        "agent": "Continuously scan KPIs, segments, channels, markets, products, and journey stages for meaningful changes.",
        "jane": "Define important KPIs, thresholds, customer segments, seasonality, benchmarks, and false-positive guardrails.",
        "boundary": "A signal is an observation, not a diagnosis or recommendation.",
        "views": {
            "CRM Leader": "Drop in repeat purchase, email engagement, activation, churn risk, segment movement.",
            "Executive": "Material revenue, conversion, retention, market, or investment changes requiring attention.",
            "Product": "Journey drop-offs, adoption shifts, unusual behavior, experience breakpoints.",
            "Integrated Marketing": "Cross-channel gaps: awareness rising while consideration or conversion weakens.",
            "Campaign / Performance Marketing": "CPA/ROAS movement, audience fatigue, conversion changes, spend anomalies.",
            "Agency": "Which clients/campaigns need attention today and why.",
        },
    },
    {
        "step": 4,
        "name": "Customer & Journey Interpretation",
        "agent": "Connect signals to likely customer state and preserve intent across touchpoints.",
        "jane": "Feed journey frameworks, segmentation, VOC, research, and customer-behavior context.",
        "boundary": "AI may infer likely journey state, but uncertainty must be visible and sensitive traits are not inferred.",
        "views": {
            "CRM Leader": "Who needs onboarding, nurture, reactivation, retention, or next-best action.",
            "Executive": "Where customers are getting stuck and which stage has the largest economic opportunity.",
            "Product": "What the customer is trying to accomplish and what is blocking the next action.",
            "Integrated Marketing": "Which message/channel should answer the customer’s next question.",
            "Campaign / Performance Marketing": "Whether traffic is low intent, high intent, or being lost after the click.",
            "Agency": "How media intent carries into the client’s site and downstream journey.",
        },
    },
    {
        "step": 5,
        "name": "Diagnosis",
        "agent": "Generate competing explanations and identify the smallest analysis that can distinguish between them.",
        "jane": "Add business history, known product changes, prior research, channel roles, and customer context.",
        "boundary": "Never jump from metric change directly to campaign action.",
        "views": {
            "CRM Leader": "Is the issue message, timing, eligibility, journey friction, or audience state?",
            "Executive": "Is the constraint acquisition, conversion, retention, product, pricing, or experience?",
            "Product": "Is friction caused by UX, technical error, content, product availability, or intent mismatch?",
            "Integrated Marketing": "Is the gap creative, audience, channel mix, landing experience, or offer?",
            "Campaign / Performance Marketing": "Is performance loss from traffic quality, auction dynamics, creative, or downstream conversion?",
            "Agency": "What is actually driving the client KPI shift, not just which channel moved.",
        },
    },
    {
        "step": 6,
        "name": "Hypothesis Generation",
        "agent": "Create and rank multiple testable hypotheses by evidence strength, impact, and cost to validate.",
        "jane": "Challenge plausibility, add missing hypotheses, and prioritize those that would change a decision.",
        "boundary": "Hypotheses remain separate from observed facts.",
        "views": {
            "CRM Leader": "Ranked lifecycle and personalization hypotheses.",
            "Executive": "Ranked growth opportunities with confidence and unknowns.",
            "Product": "Ranked friction hypotheses tied to journey evidence.",
            "Integrated Marketing": "Ranked audience/message/channel/landing hypotheses.",
            "Campaign / Performance Marketing": "Ranked optimization hypotheses with expected diagnostic value.",
            "Agency": "Client-ready hypotheses with evidence and what would prove/disprove each one.",
        },
    },
    {
        "step": 7,
        "name": "Continuous Exploration & Lightweight Testing",
        "agent": "Run SQL/Python cuts continuously across segment x channel x geo x campaign x product x journey stage.",
        "jane": "Define valid methods, sample rules, minimum volume, thresholds, and when an automated test is meaningful.",
        "boundary": "Automated exploration can find patterns; it cannot establish causal lift by itself.",
        "views": {
            "CRM Leader": "Which segments respond differently to nurture, offers, timing, and channels.",
            "Executive": "Which business levers consistently show the largest opportunity signals.",
            "Product": "Which journeys, cohorts, devices, or experiences show repeatable friction patterns.",
            "Integrated Marketing": "Which audience-channel-message combinations deserve formal testing.",
            "Campaign / Performance Marketing": "Hundreds of audience, creative, geo, and landing combinations screened automatically.",
            "Agency": "Always-on triage across campaigns and clients instead of monthly manual deep dives.",
        },
    },
    {
        "step": 8,
        "name": "Experimentation & Validation",
        "agent": "Propose experiments, holdouts, incrementality tests, or deeper statistical analyses.",
        "jane": "Own experimental design, statistical validity, causal interpretation, business guardrails, and stopping rules.",
        "boundary": "Humans own causal claims and experiment validity.",
        "views": {
            "CRM Leader": "Test nurture copy, cadence, offer, personalization, sign-in or retention interventions.",
            "Executive": "Validate whether a strategic investment creates incremental value before scaling.",
            "Product": "A/B test UX, CTA, recommendation, landing, or checkout changes.",
            "Integrated Marketing": "Test creative theme, message, landing experience, and cross-channel sequence.",
            "Campaign / Performance Marketing": "Incrementality, geo holdouts, bid/creative tests, landing-page experiments.",
            "Agency": "Design credible client tests that move beyond platform-reported attribution.",
        },
    },
    {
        "step": 9,
        "name": "Recommendation & Prioritization",
        "agent": "Synthesize evidence into actions, trade-offs, opportunity size, confidence, and next-best steps.",
        "jane": "Apply customer impact, economics, feasibility, strategic fit, and cross-functional context.",
        "boundary": "AI recommends; accountable humans decide.",
        "views": {
            "CRM Leader": "Who to contact, when, with what treatment, and what to test next.",
            "Executive": "Top 3 decisions, expected impact, confidence, risks, and evidence still missing.",
            "Product": "Which friction to fix first and the customer/business impact of doing so.",
            "Integrated Marketing": "Which journey intervention should be prioritized across channels.",
            "Campaign / Performance Marketing": "Where to shift attention or budget, with evidence and guardrails.",
            "Agency": "Client recommendation with rationale, alternatives, and evidence to inspect.",
        },
    },
    {
        "step": 10,
        "name": "Activation",
        "agent": "Support workflows, targeting logic, personalization, briefs, alerts, and next-best-action execution.",
        "jane": "Check customer relevance, brand implications, feasibility, and whether the action preserves journey intent.",
        "boundary": "High-impact customer, budget, product, and brand decisions require human approval.",
        "views": {
            "CRM Leader": "Trigger nurture, retention, reactivation, or personalized lifecycle workflows.",
            "Executive": "Approve investment, roadmap, or cross-functional action.",
            "Product": "Prioritize experience fixes, experiments, or recommendation logic.",
            "Integrated Marketing": "Coordinate channel, content, landing, CRM, and product touchpoints.",
            "Campaign / Performance Marketing": "Adjust audiences, bids, creative, landing pages, or budget.",
            "Agency": "Turn insight into client-ready media, creative, measurement, or journey actions.",
        },
    },
    {
        "step": 11,
        "name": "Outcome Measurement",
        "agent": "Monitor leading indicators, conversion, ROI, customer experience, retention, and guardrail metrics after action.",
        "jane": "Predefine success/failure, interpret trade-offs, and verify whether the intended behavior actually changed.",
        "boundary": "Do not cherry-pick whichever metric improved after launch.",
        "views": {
            "CRM Leader": "Did retention, engagement, conversion, or lifecycle progression improve?",
            "Executive": "Did the decision create incremental business value without damaging guardrails?",
            "Product": "Did the experience change improve progression and customer outcomes?",
            "Integrated Marketing": "Did the full journey improve, not just the media KPI?",
            "Campaign / Performance Marketing": "Did optimization improve efficiency and downstream conversion?",
            "Agency": "Did the recommendation work for the client, and where did impact appear?",
        },
    },
    {
        "step": 12,
        "name": "Learning & Knowledge",
        "agent": "Store validated findings, rejected hypotheses, experiment results, and reusable decision playbooks; re-check them over time.",
        "jane": "Decide what is trustworthy enough to become reusable organizational knowledge and when prior learning has expired.",
        "boundary": "Unvalidated hypotheses never become organizational truth; all learnings carry context, date, and confidence.",
        "views": {
            "CRM Leader": "Reusable lifecycle playbooks by segment and state.",
            "Executive": "Institutional memory of what growth levers worked, where, and with what confidence.",
            "Product": "Reusable evidence on friction, journey behavior, and successful interventions.",
            "Integrated Marketing": "Cross-channel learning library by audience, journey stage, and message.",
            "Campaign / Performance Marketing": "Test history, winning patterns, failed hypotheses, and conditions for reuse.",
            "Agency": "Client learning base that prevents repeating the same analysis every quarter.",
        },
    },
]

role = st.sidebar.selectbox("View the loop as", ROLES)
st.sidebar.markdown("**Core evidence labels**")
st.sidebar.write("Observed -> Inferred -> Unknown -> Recommended -> Validated / Rejected")

st.subheader("Continuous loop")
loop_names = " -> ".join([x["name"] for x in LAYERS]) + " -> Business Objective"
st.code(loop_names, language="text")

st.markdown(
    "**Scale advantage:** AI can continuously screen and re-test hundreds of combinations, while humans focus limited attention on deeper validation, experimentation, judgment, and decisions."
)

st.subheader(f"What a {role} sees at each layer")
rows = []
for layer in LAYERS:
    rows.append({
        "#": layer["step"],
        "Layer": layer["name"],
        f"{role} view": layer["views"][role],
        "Jane feeds / checks": layer["jane"],
        "Boundary": layer["boundary"],
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.subheader("Layer-by-layer detail")
for layer in LAYERS:
    with st.expander(f"{layer['step']}. {layer['name']}", expanded=layer['step'] <= 3):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Agent role**")
            st.write(layer["agent"])
            st.markdown(f"**What {role} sees**")
            st.write(layer["views"][role])
        with c2:
            st.markdown("**Jane feeds / checks**")
            st.write(layer["jane"])
            st.markdown("**Human / evidence boundary**")
            st.write(layer["boundary"])

st.subheader("Decision card")
st.markdown(
    "Every role should receive the same decision structure, but with role-specific evidence and action scope:"
)
st.markdown(
    "**Signal** -> **Context** -> **Hypothesis** -> **Recommendation / Test** -> **Evidence to inspect** -> **Confidence & unknowns** -> **Owner / action** -> **Outcome**"
)

st.subheader("Why this model is different")
st.markdown(
    "The agent is not a chatbot at the end of the analytics stack. It is a horizontal intelligence layer across the entire ecosystem. "
    "It continuously observes, tests, learns, and re-checks prior conclusions, while humans define trusted evidence, customer context, causal standards, and accountability."
)
