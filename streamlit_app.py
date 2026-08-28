import os
import re

import pandas as pd
import streamlit as st

from marketing_intelligence_agent import BusinessContext, KPIObservation, MarketingIntelligenceAgent
from marketing_intelligence_agent.llm.openai_provider import OpenAISynthesisProvider

try:
    from snowflake.snowpark.context import get_active_session
except Exception:  # local mode
    get_active_session = None


st.set_page_config(page_title="Marketing Intelligence Agent", layout="wide")
st.title("Marketing Intelligence Agent")
st.caption(
    "Snowflake-native decision support: trusted KPI data -> deterministic diagnosis -> optional OpenAI synthesis -> human judgment."
)


def active_snowflake_session():
    if get_active_session is None:
        return None
    try:
        return get_active_session()
    except Exception:
        return None


def get_openai_key():
    """Use a Snowflake secret when deployed in Snowflake; fall back to a local env var."""
    try:
        import _snowflake

        return _snowflake.get_generic_secret_string("openai_key")
    except Exception:
        return os.getenv("OPENAI_API_KEY")


def valid_table_name(name: str) -> bool:
    # Allows DATABASE.SCHEMA.TABLE and quoted/simple Snowflake identifiers.
    return bool(re.fullmatch(r'[A-Za-z0-9_.$"]+(\.[A-Za-z0-9_.$"]+){0,2}', name.strip()))


session = active_snowflake_session()
in_snowflake = session is not None

with st.sidebar:
    st.header("Business context")
    st.caption("Running inside Snowflake" if in_snowflake else "Running locally")
    objective = st.text_area(
        "Business objective",
        value="Understand why revenue growth is below target and identify the next decision-changing analysis.",
        height=120,
    )
    customer_segment = st.text_input("Customer segment", value="all")
    journey_stage = st.text_input("Journey stage (optional)", value="")
    constraints_text = st.text_area(
        "Constraints (one per line)",
        value=(
            "Do not infer causality from observational KPI movement alone.\n"
            "Do not recommend acquisition before identifying the binding funnel constraint."
        ),
        height=120,
    )
    use_openai = st.checkbox("Use OpenAI synthesis", value=False)

st.subheader("1. Load KPI data")
source_options = ["Sample data", "Upload CSV"]
if in_snowflake:
    source_options.insert(0, "Snowflake table")
source = st.radio("Data source", source_options, horizontal=True)

if source == "Snowflake table":
    table_name = st.text_input(
        "Fully qualified KPI table",
        placeholder="MY_DB.MY_SCHEMA.MARKETING_KPIS",
        help="Expected columns: metric, current, prior; optional: segment, channel.",
    )
    if table_name:
        if not valid_table_name(table_name):
            st.error("Please enter a valid Snowflake table identifier.")
            st.stop()
        query = f'SELECT metric, current, prior, segment, channel FROM {table_name}'
        try:
            df = session.sql(query).to_pandas()
            df.columns = [c.lower() for c in df.columns]
        except Exception as exc:
            st.error(f"Could not read the Snowflake table: {exc}")
            st.stop()
    else:
        st.info("Enter a Snowflake table name to continue.")
        st.stop()
elif source == "Upload CSV":
    uploaded = st.file_uploader("Upload a CSV", type=["csv"])
    if uploaded is None:
        st.info("Upload a CSV to continue.")
        st.stop()
    df = pd.read_csv(uploaded)
else:
    try:
        df = pd.read_csv("data/synthetic_kpis.csv")
    except Exception:
        df = pd.DataFrame(
            [
                {"metric": "revenue", "current": 92, "prior": 100, "segment": "all", "channel": None},
                {"metric": "search_traffic", "current": 112, "prior": 100, "segment": "all", "channel": "search"},
                {"metric": "checkout_conversion", "current": 0.255, "prior": 0.30, "segment": "all", "channel": None},
                {"metric": "returning_conversion", "current": 0.20, "prior": 0.25, "segment": "returning", "channel": None},
            ]
        )

st.dataframe(df, use_container_width=True)

required = {"metric", "current", "prior"}
missing = required - set(df.columns)
if missing:
    st.error(f"Data is missing required columns: {', '.join(sorted(missing))}")
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
            api_key = get_openai_key()
            if not api_key:
                st.error(
                    "OpenAI is not configured. In Snowflake, bind a GENERIC_STRING secret to the alias 'openai_key' "
                    "and allow api.openai.com through an external access integration."
                )
                st.stop()
            provider = OpenAISynthesisProvider(api_key=api_key)
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
