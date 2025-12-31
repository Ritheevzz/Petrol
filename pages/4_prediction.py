import streamlit as st
import pandas as pd
from utils.db import get_connection

st.set_page_config(layout="wide")

st.title("🔮 Fuel Price & Stock Prediction")
st.caption("Data-driven prediction using historical sales and price trends")

# --------------------------------------------------
# LOAD DATA FROM MYSQL
# --------------------------------------------------
engine = get_connection()

price_df = pd.read_sql("""
    SELECT date, fuel_type, selling_price
    FROM fuel_price
    ORDER BY date
""", engine)

sales_df = pd.read_sql("""
    SELECT date, fuel_type, quantity_sold
    FROM fuel_sales
    ORDER BY date
""", engine)

price_df["date"] = pd.to_datetime(price_df["date"])
sales_df["date"] = pd.to_datetime(sales_df["date"])

# --------------------------------------------------
# USER INPUT
# --------------------------------------------------
fuel = st.selectbox("Select Fuel Type", ["Petrol", "Diesel"])

fuel_price_df = price_df[price_df["fuel_type"] == fuel].copy()
fuel_sales_df = sales_df[sales_df["fuel_type"] == fuel].copy()

if len(fuel_price_df) < 30 or len(fuel_sales_df) < 30:
    st.warning("⚠️ Not enough historical data for prediction.")
    st.stop()

# --------------------------------------------------
# PRICE PREDICTION (TREND-BASED)
# --------------------------------------------------
fuel_price_df = fuel_price_df.sort_values("date")

fuel_price_df["ma_7"] = fuel_price_df["selling_price"].rolling(7).mean()
fuel_price_df["ma_30"] = fuel_price_df["selling_price"].rolling(30).mean()

latest_price = fuel_price_df.iloc[-1]["selling_price"]
avg_price = fuel_price_df["selling_price"].mean()

# Recent trend (last 7 days)
recent_trend = fuel_price_df["selling_price"].diff().tail(7).mean()
predicted_price = latest_price + recent_trend

# --------------------------------------------------
# DISPLAY PRICE METRICS
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Price (₹)", f"{latest_price:.2f}")

with col2:
    st.metric("Average Price (₹)", f"{avg_price:.2f}")

with col3:
    st.metric("Predicted Tomorrow Price (₹)", f"{predicted_price:.2f}")

# --------------------------------------------------
# DEMAND ANALYSIS (FROM SALES DATA)
# --------------------------------------------------
fuel_sales_df = fuel_sales_df.sort_values("date")

avg_daily_sales = fuel_sales_df["quantity_sold"].tail(30).mean()
recent_sales = fuel_sales_df["quantity_sold"].tail(7).mean()

# --------------------------------------------------
# STOCK PURCHASE RECOMMENDATION
# --------------------------------------------------
st.subheader("📦 Stock Purchase Recommendation")

if predicted_price < avg_price * 0.98 and recent_sales >= avg_daily_sales:
    st.success("🟢 BUY MORE STOCK")
    st.write(
        f"Price is predicted to be lower than average and demand is high.\n\n"
        f"Recommended Purchase: **High quantity** (~{int(avg_daily_sales * 7)} litres)"
    )

elif predicted_price > avg_price * 1.02:
    st.error("🔴 BUY MINIMUM STOCK")
    st.write(
        "Price is predicted to be higher than usual.\n\n"
        "Recommended Purchase: **Essential stock only**"
    )

else:
    st.warning("🟡 NORMAL PURCHASE")
    st.write(
        "Price and demand are stable.\n\n"
        f"Recommended Purchase: **Routine quantity** (~{int(avg_daily_sales * 5)} litres)"
    )

# --------------------------------------------------
# MARKET PRESSURE INDICATOR (DATA-DRIVEN)
# --------------------------------------------------
st.subheader("🌍 Market Demand Indicator")

if recent_sales > avg_daily_sales * 1.05:
    st.warning("🟡 High Demand Detected")
    st.write(
        "Recent fuel consumption is higher than usual. "
        "Possible price increase if demand continues."
    )

elif recent_sales < avg_daily_sales * 0.95:
    st.success("🟢 Demand Stable / Low")
    st.write(
        "Fuel demand is stable or slightly reduced. "
        "Price hikes are unlikely in the short term."
    )

else:
    st.info("ℹ️ Normal Demand Conditions")
    st.write(
        "Fuel demand is within normal range. "
        "No immediate market pressure detected."
    )

# --------------------------------------------------
# PRICE TREND VISUALIZATION
# --------------------------------------------------
st.subheader("📈 Recent Price Trend")

plot_df = fuel_price_df.tail(30).set_index("date")[["selling_price"]]
st.line_chart(plot_df, use_container_width=True)

# --------------------------------------------------
# EXPLANATION
# --------------------------------------------------
with st.expander("ℹ️ How this prediction works"):
    st.write("""
    - Predictions are based on recent historical trends.
    - Moving averages smooth short-term fluctuations.
    - Demand is inferred from actual fuel sales data.
    - The system supports **decision-making**, not exact forecasting.
    """)
