import streamlit as st
import pandas as pd
import time
from EDGAR_Pipeline import investment_watchlist, get_company_facts, extract_fsli_to_dataframe


METRIC_MAPPING = {
    "Total Assets": {"us-gaap": ["Assets"], "ifrs-full": ["Assets"]},
    "Total Equity": {"us-gaap": ["StockholdersEquity"], "ifrs-full": ["Equity"]},
    "Liabilities": {"us-gaap": ["Liabilities"], "ifrs-full": ["Liabilities"]},
    "Total Income": {"us-gaap": ["NetIncomeLoss"], "ifrs-full": ["ProfitLoss"]},
    "Total Revenue": {
        "us-gaap": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "ifrs-full": ["Revenue"]
    }
}

def get_latest_value(df: pd.DataFrame) -> float:
    """Helper to extract the most recent annual (10-K/20-F) or trailing value from the extracted dataframe."""
    if df.empty:
        return None

    # Filter for full-year / annual reports to maintain comparability, or fall back to latest form
    annuals = df[df["form"].isin(["10-K", "20-F"])]
    target_df = annuals if not annuals.empty else df

    # Sort by fiscal year and fiscal period to get the latest data point
    target_df = target_df.sort_values(by=["fy", "fp"], ascending=[False, False])
    return target_df.iloc[0]["val"]

# ---------- Page setup ----------
st.set_page_config(page_title="Aperture Insights — EDGAR Pipeline", layout="wide")

st.title("Aperture Insights: Live EDGAR Data Pipeline")
st.caption("Pull SEC filing data for companies on watchlist via the Company Facts API.")

# ---------- Cached data fetch ----------
@st.cache_data(ttl=3600)
def cached_get_company_facts(cik: str, user_agent: str) -> dict:
    return get_company_facts(cik, user_agent)

# ---------- Sidebar: inputs ----------
watchlist_df = investment_watchlist()

st.sidebar.header("Query the Pipeline")
selected_company = st.sidebar.selectbox("Company", watchlist_df["company_name"])
selected_metric = st.sidebar.selectbox("Financial Metric", list(METRIC_MAPPING.keys()))
pull_button = st.sidebar.button("Pull Data")

selected_row = watchlist_df[watchlist_df["company_name"] == selected_company].iloc[0]
cik = selected_row["cik"]
ticker = selected_row["ticker"]
category = selected_row["category"]

# ---------- Main panel ----------
if pull_button:
    with st.spinner(f"Connecting to EDGAR for {selected_company}..."):
        try:
            company_json = cached_get_company_facts(cik, st.secrets["USER_AGENT"])
        except Exception as e:
            st.error(f"Could not retrieve SEC data for {ticker}: {e}")
            st.stop()

    facts = company_json.get("facts", {})
    standard = "us-gaap" if "us-gaap" in facts else "ifrs-full" if "ifrs-full" in facts else None

    if not standard:
        st.warning(f"No recognized accounting standard found for {ticker}.")
        st.stop()

    # Try each candidate tag until one returns data (the Vertiv fix)
    candidates = METRIC_MAPPING[selected_metric][standard]
    metric_df = pd.DataFrame()
    used_tag = None
    for fsli_key in candidates:
        metric_df = extract_fsli_to_dataframe(company_json, fsli_key)
        if not metric_df.empty:
            used_tag = fsli_key
            break

    st.subheader(f"{selected_company} ({ticker}) — {selected_metric}")
    st.caption(f"Filer type: {category.upper()}  |  Standard: {standard}  |  XBRL tag: {used_tag or 'not found'}")

    if metric_df.empty:
        st.warning(f"No data found for '{selected_metric}' — this company may tag it differently.")
    else:
        # Latest headline number
        latest = get_latest_value(metric_df)
        if latest is not None:
            st.metric(label=f"Latest reported {selected_metric}", value=f"${latest:,.0f}")

        # Full table
        st.dataframe(metric_df, use_container_width=True)

        # Trend chart from annual filings
        annuals = metric_df[metric_df["form"].isin(["10-K", "20-F"])]
        chart_source = annuals if not annuals.empty else metric_df
        chart_df = chart_source[["end", "val"]].dropna().drop_duplicates(subset="end").sort_values("end")
        if len(chart_df) > 1:
            st.line_chart(chart_df.set_index("end"))
else:
    st.info("Select a company and metric in the sidebar, then click **Pull Data**.")