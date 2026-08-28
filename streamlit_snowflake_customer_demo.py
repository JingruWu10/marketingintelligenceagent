import pandas as pd
import streamlit as st

from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Marketing Intelligence Agent", layout="wide")
st.title("Marketing Intelligence Agent")
st.caption("Snowflake-native promotion and sales diagnosis with explicit evidence boundaries.")

session = get_active_session()

with st.sidebar:
    st.header("Business question")
    objective = st.text_area(
        "Objective",
        "Which promotion patterns are associated with stronger sales and profit, and what should we investigate next?",
        height=100,
    )
    row_limit = st.selectbox("Transactions to analyze", [10000, 50000, 100000], index=1)

st.info("The demo uses Snowflake TPC-DS CUSTOMER, STORE_SALES, and PROMOTION directly. Results are observational associations, not causal lift.")

query = f"""
WITH sales_sample AS (
    SELECT
        SS_CUSTOMER_SK,
        SS_PROMO_SK,
        SS_QUANTITY,
        SS_EXT_SALES_PRICE,
        SS_EXT_DISCOUNT_AMT,
        SS_COUPON_AMT,
        SS_NET_PAID,
        SS_NET_PROFIT
    FROM SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.STORE_SALES
    WHERE SS_CUSTOMER_SK IS NOT NULL
    LIMIT {row_limit}
)
SELECT
    s.SS_CUSTOMER_SK,
    c.C_PREFERRED_CUST_FLAG,
    s.SS_PROMO_SK,
    COALESCE(p.P_PROMO_NAME, 'No matched promotion') AS PROMO_NAME,
    COALESCE(p.P_DISCOUNT_ACTIVE, 'N') AS DISCOUNT_ACTIVE,
    COALESCE(p.P_CHANNEL_EMAIL, 'N') AS CHANNEL_EMAIL,
    COALESCE(p.P_CHANNEL_DMAIL, 'N') AS CHANNEL_DMAIL,
    COALESCE(p.P_CHANNEL_TV, 'N') AS CHANNEL_TV,
    COALESCE(p.P_CHANNEL_RADIO, 'N') AS CHANNEL_RADIO,
    COALESCE(p.P_CHANNEL_PRESS, 'N') AS CHANNEL_PRESS,
    COALESCE(p.P_CHANNEL_EVENT, 'N') AS CHANNEL_EVENT,
    COALESCE(p.P_CHANNEL_DEMO, 'N') AS CHANNEL_DEMO,
    p.P_COST,
    p.P_RESPONSE_TARGET,
    s.SS_QUANTITY,
    s.SS_EXT_SALES_PRICE,
    s.SS_EXT_DISCOUNT_AMT,
    s.SS_COUPON_AMT,
    s.SS_NET_PAID,
    s.SS_NET_PROFIT
FROM sales_sample s
LEFT JOIN SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CUSTOMER c
    ON s.SS_CUSTOMER_SK = c.C_CUSTOMER_SK
LEFT JOIN SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.PROMOTION p
    ON s.SS_PROMO_SK = p.P_PROMO_SK
"""

@st.cache_data(show_spinner=False)
def load_data(sql):
    data = session.sql(sql).to_pandas()
    data.columns = [c.lower() for c in data.columns]
    return data

try:
    df = load_data(query)
except Exception as exc:
    st.error(f"Snowflake query failed: {exc}")
    st.stop()

st.subheader("1. Trusted joined data")
st.dataframe(df.head(50), use_container_width=True)

matched = df["ss_promo_sk"].notna() & df["promo_name"].ne("No matched promotion")
matched_df = df.loc[matched].copy()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Transactions", f"{len(df):,}")
c2.metric("Net sales", f"${df['ss_net_paid'].sum():,.0f}")
c3.metric("Net profit", f"${df['ss_net_profit'].sum():,.0f}")
c4.metric("Promo-linked rows", f"{matched.mean():.1%}")

st.subheader("2. Promotion vs. no matched promotion")
df["promotion_status"] = matched.map({True: "Matched promotion", False: "No matched promotion"})
summary = (
    df.groupby("promotion_status", dropna=False)
    .agg(
        transactions=("ss_customer_sk", "size"),
        customers=("ss_customer_sk", "nunique"),
        avg_net_paid=("ss_net_paid", "mean"),
        avg_net_profit=("ss_net_profit", "mean"),
        avg_discount=("ss_ext_discount_amt", "mean"),
        avg_quantity=("ss_quantity", "mean"),
    )
    .reset_index()
)
st.dataframe(summary, use_container_width=True)

if not matched_df.empty:
    st.subheader("3. Promotion pattern diagnostics")
    discount_summary = (
        matched_df.groupby("discount_active", dropna=False)
        .agg(
            transactions=("ss_customer_sk", "size"),
            avg_net_paid=("ss_net_paid", "mean"),
            avg_net_profit=("ss_net_profit", "mean"),
            avg_discount=("ss_ext_discount_amt", "mean"),
        )
        .reset_index()
    )
    st.markdown("**Discount-active promotions**")
    st.dataframe(discount_summary, use_container_width=True)

    channel_cols = {
        "channel_email": "Email",
        "channel_dmail": "Direct mail",
        "channel_tv": "TV",
        "channel_radio": "Radio",
        "channel_press": "Press",
        "channel_event": "Event",
        "channel_demo": "Demo",
    }
    rows = []
    for col, label in channel_cols.items():
        active = matched_df[col].astype(str).str.upper().eq("Y")
        if active.any():
            rows.append(
                {
                    "channel_flag": label,
                    "transactions": int(active.sum()),
                    "avg_net_paid": matched_df.loc[active, "ss_net_paid"].mean(),
                    "avg_net_profit": matched_df.loc[active, "ss_net_profit"].mean(),
                    "avg_discount": matched_df.loc[active, "ss_ext_discount_amt"].mean(),
                }
            )
    channel_summary = pd.DataFrame(rows).sort_values("avg_net_profit", ascending=False) if rows else pd.DataFrame()
    st.markdown("**Promotion channel flags**")
    st.dataframe(channel_summary, use_container_width=True)

    st.subheader("4. Customer segment lens")
    preferred_summary = (
        matched_df.groupby("c_preferred_cust_flag", dropna=False)
        .agg(
            transactions=("ss_customer_sk", "size"),
            customers=("ss_customer_sk", "nunique"),
            avg_net_paid=("ss_net_paid", "mean"),
            avg_net_profit=("ss_net_profit", "mean"),
            avg_discount=("ss_ext_discount_amt", "mean"),
        )
        .reset_index()
    )
    st.dataframe(preferred_summary, use_container_width=True)

st.subheader("5. Decision layer")
st.markdown(f"**Objective:** {objective}")

if matched_df.empty:
    st.warning("No promotion records matched this transaction sample. Increase the transaction sample or inspect promotion-key coverage before drawing conclusions.")
else:
    promo_profit = matched_df["ss_net_profit"].mean()
    no_promo_profit = df.loc[~matched, "ss_net_profit"].mean() if (~matched).any() else None
    st.markdown("**OBSERVED**")
    st.write(f"- {matched.mean():.1%} of sampled transactions have a matched promotion record.")
    st.write(f"- Promotion-linked transactions average ${promo_profit:,.2f} net profit in this sample.")
    if no_promo_profit is not None:
        st.write(f"- Transactions without a matched promotion average ${no_promo_profit:,.2f} net profit.")

    st.markdown("**INFERRED / HYPOTHESES TO TEST**")
    st.write("- Differences across promotion flags may reflect customer mix, product mix, timing, or promotion design rather than incremental promotion impact.")
    st.write("- Discounting may increase transaction value or quantity while creating a margin tradeoff; compare profit, not revenue alone.")

    st.markdown("**UNKNOWN**")
    st.write("- We do not have a randomized holdout here, so this analysis cannot establish causal lift.")
    st.write("- Channel flags describe promotion configuration; they do not prove that an individual customer was actually exposed to that channel.")

    st.markdown("**RECOMMENDED NEXT ANALYSIS**")
    st.write("1. Segment by promotion type, customer status, product/category, and time period.")
    st.write("2. Compare net sales and net profit together to identify revenue-margin tradeoffs.")
    st.write("3. Add an experiment/holdout or another credible causal design before calling the difference incremental ROI.")

with st.expander("SQL used by the app"):
    st.code(query, language="sql")
