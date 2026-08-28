import os

import pandas as pd
import streamlit as st

from marketing_intelligence_agent import BusinessContext, KPIObservation, MarketingIntelligenceAgent
from marketing_intelligence_agent.llm.openai_provider import OpenAISynthesisProvider


st.set_page_config(page_title="Marketing Intelligence Agent", layout="wide")
st.title("Marketing Intelligence Agent")
st.caption("AI-assisted diagnosis with deterministic guardrails and human judgment in the loop.")

with st.sidebar:
    st.header("Business context")
    objective = st.text_area(
        "Business objective",
        value="Understand why revenue growth is below target and identify the next decision-changing analysis.",
        height=120,
    )
    customer_segment = st.text_input("Customer segment", value="all")
    journey_stage = st.text_input("Journey stage (optional)", value="")
    constraints_text = st.text_area(
        "Constraints (one per line)",
        value="Do not infer causality from observational KPI movement alone.\nDo not recommend acquisition before identifying the binding funnel constraint.",
        height=120,
    )
    use_openai = st.checkbox("Use OpenAI synthesis", value=False)

st.subheader("1. Load KPI data")
uploaded = st.file_uploader("Upload a CSV", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded)
else:
    st.info("No file uploaded. Using the sample KPI dataset from the repository.")
    df = pd.read_csv("data/synthetic_kpis.csv")

st.dataframe(df, use_container_width=True)

required = {"metric", "current", "prior"}
missing = required - set(df.columns)
if missing:
    st.error(f"CSV is missing required columns: {', '.join(sorted(missing))}")
    st.stop()

for optional_col, default in [("segment", "all"), ("channel", None)]:
    if optional_col not in df.columns:
        df[optional_col] = default

st.subheader("2. Analyze")
if st.button("Run analysis", type="primary"):
    try:
        observations = [KPIObservation(**row) for row in df.to_dict(orient="records")]
        constraints = [x.strip() for x in constraints_text.splitlines() if x.strip()]
        context = BusinessContext(
            objective=objective,
            customer_segment=customer_segment or "all",
            journey_stage=journey_stage or None,
            constraints=constraints,
        )

        agent = MarketingIntelligenceAgent()

        if use_openai:
            if not os.getenv("OPENAI_API_KEY"):
                st.error("OPENAI_API_KEY is not set. Add it to your local environment or Streamlit secrets before using OpenAI synthesis.")
                st.stop()
            provider = OpenAISynthesisProvider()
            result = agent.analyze_with_ai(context, observations, provider)
        else:
            result = agent.analyze(context, observations)

        st.subheader("3. Decision output")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### What changed")
            for item in result.what_changed:
                st.write(f"- {item}")

            st.markdown("### Where in the journey")
            st.write(result.where_in_journey)

            st.markdown("### What to check next")
            for item in result.what_to_check_next:
                st.write(f"- {item}")

        with col2:
            st.markdown("### Hypotheses")
            for i, h in enumerate(result.hypotheses, start=1):
                st.write(f"**{i}. {h.statement}**")
                st.caption(f"Confidence: {h.confidence}")
                if h.evidence_needed:
                    st.write("Evidence needed:")
                    for e in h.evidence_needed:
                        st.write(f"- {e}")

            st.markdown("### Recommendation")
            st.write(result.recommendation.action)
            st.write(f"**Owner:** {result.recommendation.owner}")
            st.write(f"**Primary KPI:** {result.recommendation.primary_kpi}")
            if result.recommendation.leading_indicator:
                st.write(f"**Leading indicator:** {result.recommendation.leading_indicator}")
            if result.recommendation.guardrail:
                st.write(f"**Guardrail:** {result.recommendation.guardrail}")

        st.markdown("### Evidence classification")
        evidence_df = pd.DataFrame([e.model_dump() for e in result.evidence])
        st.dataframe(evidence_df, use_container_width=True)

        with st.expander("Raw structured output"):
            st.json(result.model_dump())

    except Exception as exc:
        st.exception(exc)
