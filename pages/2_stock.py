import streamlit as st
import pandas as pd
from utils.db import get_connection

st.set_page_config(layout="wide")

st.title("📦 Stock Dashboard")

engine = get_connection()

# --------------------------------------------------
# LOAD STOCK DATA
# --------------------------------------------------
stock_df = pd.read_sql("SELECT * FROM vw_fuel_stock", engine)
stock_df['date'] = pd.to_datetime(stock_df['date'])

# Helpers
stock_df['year'] = stock_df['date'].dt.year
stock_df['month_name'] = stock_df['date'].dt.month_name()
stock_df['month_num'] = stock_df['date'].dt.month

# --------------------------------------------------
# SIDEBAR FILTERS (Fuel applies to whole page)
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

fuel_type = st.sidebar.selectbox(
    "Fuel Type",
    ["Petrol", "Diesel"]
)

# ==================================================
# 🟦 CURRENT STOCK SNAPSHOT (UNFILTERED)
# ==================================================
st.subheader("🟦 Current Stock Snapshot (Latest Data)")

latest_stock_df = (
    stock_df[stock_df['fuel_type'] == fuel_type]
    .sort_values("date", ascending=False)
)

if latest_stock_df.empty:
    st.error("❌ No stock data available.")
    st.stop()

latest_row = latest_stock_df.iloc[0]

current_stock = int(latest_row['closing_stock'])
last_updated = latest_row['date'].strftime("%Y-%m-%d")

LOW_STOCK_THRESHOLD = 5000  # litres

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label=f"Current {fuel_type} Stock (Litres)",
        value=current_stock
    )

with col2:
    st.metric(
        label="Last Updated Date",
        value=last_updated
    )

# ---- Stock Health Indicator ----
if current_stock < LOW_STOCK_THRESHOLD:
    st.error(
        f"🚨 LOW STOCK ALERT: {fuel_type} stock is below {LOW_STOCK_THRESHOLD} litres!"
    )
else:
    st.success(
        f"✅ Stock level is healthy for {fuel_type}"
    )

# --------------------------------------------------
# DIVIDER BETWEEN CURRENT & ANALYSIS
# --------------------------------------------------
st.markdown("---")
st.subheader("🟨 Historical Stock Analysis")

# --------------------------------------------------
# YEAR & MONTH FILTERS (ANALYSIS ONLY)
# --------------------------------------------------
year = st.sidebar.selectbox(
    "Select Year",
    sorted(stock_df['year'].unique())
)

available_months = (
    stock_df[stock_df['year'] == year]
    .sort_values('month_num')['month_name']
    .unique()
)

selected_months = st.sidebar.multiselect(
    "Select Month",
    available_months,
    default=available_months
)

# Defensive UX: no month selected → full year
if not selected_months:
    selected_months = available_months

# --------------------------------------------------
# APPLY FILTERS FOR ANALYSIS
# --------------------------------------------------
filtered_stock = stock_df[
    (stock_df['fuel_type'] == fuel_type) &
    (stock_df['year'] == year) &
    (stock_df['month_name'].isin(selected_months))
]

if filtered_stock.empty:
    st.warning("⚠️ No stock data available for the selected filters.")
    st.stop()

# --------------------------------------------------
# STOCK TREND
# --------------------------------------------------
st.subheader("📈 Stock Level Trend")

st.line_chart(
    filtered_stock
    .sort_values("date")
    .set_index("date")["closing_stock"],
    use_container_width=True
)

# --------------------------------------------------
# RAW DATA
# --------------------------------------------------
st.markdown("---")

with st.expander("📄 View Stock Data"):
    st.dataframe(
        filtered_stock
        .sort_values("date", ascending=False),
        use_container_width=True
    )