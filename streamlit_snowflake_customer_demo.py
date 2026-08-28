import pandas as pd
import streamlit as st

try:
    from snowflake.snowpark.context import get_active_session
except Exception:
    get_active_session = None


st.set_page_config(page_title="Customer Intelligence Demo", layout="wide")
st.title("Customer Intelligence Demo")
st.caption("Snowflake-native customer profiling using TPC-DS sample data. Descriptive only: no causal or sensitive-trait inference.")


def get_session():
    if get_active_session is None:
        return None
    try:
        return get_active_session()
    except Exception:
        return None


def pct(n, d):
    return float(n / d) if d else 0.0


session = get_session()
if session is None:
    st.error("This demo is designed to run inside Streamlit in Snowflake.")
    st.stop()

with st.sidebar:
    st.header("Demo settings")
    table_name = st.text_input(
        "Customer table",
        value="SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CUSTOMER",
    )
    row_limit = st.slider("Rows to profile", min_value=100, max_value=10000, value=1000, step=100)

query = f"""
SELECT
    C_CUSTOMER_SK,
    C_CUSTOMER_ID,
    C_PREFERRED_CUST_FLAG,
    C_LOGIN,
    C_EMAIL_ADDRESS,
    C_CURRENT_ADDR_SK,
    C_FIRST_SALES_DATE_SK,
    C_FIRST_SHIPTO_DATE_SK,
    C_LAST_REVIEW_DATE_SK
FROM {table_name}
LIMIT {row_limit}
"""

try:
    df = session.sql(query).to_pandas()
    df.columns = [c.lower() for c in df.columns]
except Exception as exc:
    st.error(f"Could not read the Snowflake table: {exc}")
    st.stop()

st.subheader("1. Customer sample")
st.dataframe(df.head(50), use_container_width=True)

n = len(df)
preferred = df["c_preferred_cust_flag"].astype(str).str.upper().eq("Y")
has_login = df["c_login"].fillna("").astype(str).str.strip().ne("")
has_email = df["c_email_address"].fillna("").astype(str).str.strip().ne("")
has_address = df["c_current_addr_sk"].notna()
has_sales_history = df["c_first_sales_date_sk"].notna()
has_ship_history = df["c_first_shipto_date_sk"].notna()
has_review = df["c_last_review_date_sk"].notna()

metrics = pd.DataFrame(
    [
        ("Preferred-customer share", pct(preferred.sum(), n)),
        ("Login identifier coverage", pct(has_login.sum(), n)),
        ("Email coverage", pct(has_email.sum(), n)),
        ("Address-key coverage", pct(has_address.sum(), n)),
        ("First-sales history coverage", pct(has_sales_history.sum(), n)),
        ("First-ship history coverage", pct(has_ship_history.sum(), n)),
        ("Review-history coverage", pct(has_review.sum(), n)),
    ],
    columns=["metric", "rate"],
)
metrics["rate"] = metrics["rate"].round(4)

st.subheader("2. Activation-readiness profile")
cols = st.columns(4)
cols[0].metric("Customers profiled", f"{n:,}")
cols[1].metric("Preferred customer", f"{preferred.mean():.1%}")
cols[2].metric("Email available", f"{has_email.mean():.1%}")
cols[3].metric("Login available", f"{has_login.mean():.1%}")
st.dataframe(metrics, use_container_width=True)

profile = pd.DataFrame(
    {
        "segment": ["Preferred", "Non-preferred"],
        "customers": [int(preferred.sum()), int((~preferred).sum())],
        "email_coverage": [
            pct((preferred & has_email).sum(), preferred.sum()),
            pct(((~preferred) & has_email).sum(), (~preferred).sum()),
        ],
        "login_coverage": [
            pct((preferred & has_login).sum(), preferred.sum()),
            pct(((~preferred) & has_login).sum(), (~preferred).sum()),
        ],
        "sales_history_coverage": [
            pct((preferred & has_sales_history).sum(), preferred.sum()),
            pct(((~preferred) & has_sales_history).sum(), (~preferred).sum()),
        ],
        "review_history_coverage": [
            pct((preferred & has_review).sum(), preferred.sum()),
            pct(((~preferred) & has_review).sum(), (~preferred).sum()),
        ],
    }
)
for c in ["email_coverage", "login_coverage", "sales_history_coverage", "review_history_coverage"]:
    profile[c] = profile[c].round(4)

st.subheader("3. Segment comparison")
st.dataframe(profile, use_container_width=True)

st.subheader("4. What the analyst should conclude")
st.markdown(
    """
**Observed**
- This table supports descriptive customer profiling and data-readiness checks.
- We can compare preferred vs. non-preferred customers on contactability and available history fields.

**Unknown**
- This table alone does **not** tell us campaign exposure, product usage, opportunity stage, revenue, or causal response to marketing.
- We should not infer purchase intent or customer motivation from demographic attributes alone.

**Recommended next step**
- Join CUSTOMER to sales/order facts and campaign or engagement data before making GTM activation recommendations.
- Define the business objective first (acquisition, expansion, retention, or contactability), then build the minimum trusted feature set needed for that decision.
"""
)

st.subheader("5. Snowflake-native next layer")
st.code(
    """CUSTOMER
  -> trusted customer/account entity
  -> sales + campaign + engagement joins
  -> semantic metrics
  -> deterministic checks
  -> AI hypothesis/synthesis layer
  -> analyst validation and action""",
    language="text",
)
