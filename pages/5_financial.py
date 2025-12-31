import streamlit as st
import pandas as pd
from utils.db import get_connection

st.set_page_config(layout="wide")

st.title("💰 Profit & Loss Dashboard")
st.info(
    "Actual business profit calculated using buying price, selling price, "
    "quantity sold, and operational expenses."
)

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
engine = get_connection()

profit_df = pd.read_sql(
    "SELECT * FROM vw_profit_analysis",
    engine
)

profit_df["date"] = pd.to_datetime(profit_df["date"])

# --------------------------------------------------
# DATE HELPERS
# --------------------------------------------------
profit_df["year"] = profit_df["date"].dt.year
profit_df["month_name"] = profit_df["date"].dt.month_name()
profit_df["month_num"] = profit_df["date"].dt.month

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

year = st.sidebar.selectbox(
    "Select Year",
    sorted(profit_df["year"].unique())
)

available_months = (
    profit_df[profit_df["year"] == year]
    .sort_values("month_num")["month_name"]
    .unique()
)

selected_months = st.sidebar.multiselect(
    "Select Month",
    available_months,
    default=available_months
)

# If no month selected → show full year
if not selected_months:
    selected_months = available_months

fuel = st.sidebar.multiselect(
    "Fuel Type",
    profit_df["fuel_type"].unique(),
    default=profit_df["fuel_type"].unique()
)

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------
filtered_df = profit_df[
    (profit_df["year"] == year) &
    (profit_df["month_name"].isin(selected_months)) &
    (profit_df["fuel_type"].isin(fuel))
]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_margin = filtered_df["fuel_margin"].sum()
total_expense = filtered_df["total_expenses"].sum()
total_profit = filtered_df["profit"].sum()

profit_margin_pct = (
    (total_profit / total_margin) * 100
    if total_margin != 0 else 0
)

# --------------------------------------------------
# KPIs
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Fuel Margin (₹)", f"{int(total_margin):,}")

with col2:
    st.metric("Total Expenses (₹)", f"{int(total_expense):,}")

with col3:
    st.metric("Actual Profit (₹)", f"{int(total_profit):,}")

with col4:
    st.metric("Profit Margin (%)", f"{profit_margin_pct:.2f}%")

# --------------------------------------------------
# PROFIT TREND
# --------------------------------------------------
st.subheader("📈 Profit Trend Over Time")

profit_trend = (
    filtered_df
    .groupby("date")["profit"]
    .sum()
)

st.line_chart(profit_trend, use_container_width=True)

# --------------------------------------------------
# FUEL-WISE PROFIT COMPARISON
# --------------------------------------------------
st.subheader("⛽ Fuel-wise Profit Distribution")

fuel_profit = (
    filtered_df
    .groupby("fuel_type")["profit"]
    .sum()
)

st.bar_chart(fuel_profit)

# --------------------------------------------------
# MONTHLY PROFIT BAR
# --------------------------------------------------
st.subheader("📊 Monthly Profit Analysis")

monthly_profit = (
    filtered_df
    .groupby("month_name")["profit"]
    .sum()
    .reindex(available_months)
)

st.bar_chart(monthly_profit)

# --------------------------------------------------
# RAW DATA
# --------------------------------------------------
st.markdown("---")

with st.expander("📄 View Financial Data"):
    st.dataframe(
        filtered_df.sort_values("date"),
        use_container_width=True
    )

# --------------------------------------------------
# EXPLANATION
# --------------------------------------------------
with st.expander("ℹ️ How profit is calculated"):
    st.write("""
    **Profit Formula Used:**

    (Selling Price − Buying Price) × Quantity Sold − Expenses

    This reflects the **actual operational profit** of a petrol bunk,
    not just accounting profit.
    """)
