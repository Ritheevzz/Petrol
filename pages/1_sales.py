import streamlit as st
import pandas as pd
from utils.db import get_connection

st.set_page_config(layout="wide")

st.title("📊 Sales Dashboard")
st.info("Displays fuel sales performance and revenue trends.")

# ----------------------------------
# DATABASE CONNECTION
# ----------------------------------
engine = get_connection()

sales_df = pd.read_sql("SELECT * FROM vw_fuel_sales", engine)
income_df = pd.read_sql("SELECT * FROM vw_income_summary", engine)

sales_df["date"] = pd.to_datetime(sales_df["date"])
income_df["date"] = pd.to_datetime(income_df["date"])

# ----------------------------------
# MONTH HELPERS
# ----------------------------------
sales_df["month_name"] = sales_df["date"].dt.month_name()
sales_df["month_num"] = sales_df["date"].dt.month

# ----------------------------------
# SIDEBAR FILTERS
# ----------------------------------
st.sidebar.header("🔍 Filters")

year = st.sidebar.selectbox(
    "Select Year",
    sorted(sales_df["date"].dt.year.unique())
)

available_months = (
    sales_df[sales_df["date"].dt.year == year]
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
    sales_df["fuel_type"].unique(),
    default=sales_df["fuel_type"].unique()
)

# ----------------------------------
# FILTER DATA
# ----------------------------------
filtered_sales = sales_df[
    (sales_df["date"].dt.year == year) &
    (sales_df["month_name"].isin(selected_months)) &
    (sales_df["fuel_type"].isin(fuel))
]

filtered_income = income_df[
    (income_df["date"].dt.year == year) &
    (income_df["date"].dt.month_name().isin(selected_months))
]

# ----------------------------------
# KPIs
# ----------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Fuel Sold (L)",
        int(filtered_sales["quantity_sold"].sum())
    )

with col2:
    st.metric(
        "Total Sales (₹)",
        int(filtered_income["total_sales"].sum())
    )

with col3:
    st.metric(
        "Total Profit (₹)",
        int(filtered_income["profit"].sum())
    )

# ----------------------------------
# SALES TREND (SEPARATE LINE PER FUEL)
# ----------------------------------
st.subheader("📈 Fuel Sales Trend")

for f in fuel:
    temp = filtered_sales[filtered_sales["fuel_type"] == f]
    if not temp.empty:
        st.line_chart(
            temp.groupby("date")["quantity_sold"].sum(),
            use_container_width=True
        )

# ----------------------------------
# FUEL-WISE SALES BAR CHART
# ----------------------------------
st.subheader("⛽ Fuel Sales by Fuel Type")

fuel_summary = (
    filtered_sales
    .groupby("fuel_type")["quantity_sold"]
    .sum()
    .reset_index()
)

if not fuel_summary.empty:
    st.bar_chart(fuel_summary.set_index("fuel_type"))

# ----------------------------------
# RAW DATA VIEW
# ----------------------------------
st.markdown("---")

with st.expander("📄 View Raw Sales Data"):
    st.dataframe(
        filtered_sales.sort_values("date"),
        use_container_width=True
    )
