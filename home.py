import streamlit as st

st.set_page_config(
    page_title="Petrol Bunk Management System",
    layout="wide"
)

# ---------- SIDEBAR ----------
st.sidebar.title("🏠 Home")
st.sidebar.markdown("Welcome to our system")

# ---------- MAIN CONTENT ----------
st.title("⛽ ABC Fuel Station")

st.subheader("About Us")
st.write("""
ABC Fuel Station is a modern petrol bunk providing high-quality Petrol and Diesel
with real-time monitoring of sales, stock, and profits.
""")

st.subheader("📍 Location")
st.write("""
ABC Fuel Station  
NH Road, Chennai – 600001  
Tamil Nadu, India
""")

st.subheader("🛢️ Products Offered")
st.markdown("""
- Petrol  
- Diesel  
- Lubricants  
- Air & Water Services  
""")

st.subheader("🎯 Our Objective")
st.write("""
To digitize petrol bunk operations using data analytics, dashboards,
and AI-based predictions for better decision-making.
""")

st.success("⬅️ Use the sidebar to navigate to other modules")
