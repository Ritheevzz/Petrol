import streamlit as st
import pandas as pd
import json
from utils.db import get_connection
import google.generativeai as genai

# ---------------- CONFIG ----------------
GEMINI_API_KEY = "AIzaSyCrwOwusI33_UZxi9oVWnQKqi2pCmgkChA"
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")
engine = get_connection()

st.set_page_config(layout="wide")
st.title("🤖 Intelligent Business Assistant (Beta Version)")
st.caption("SQL-grounded chatbot for petrol bunk analytics")
st.info("Currently Under Development")


# ---------------- SESSION STATE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- HELPERS ----------------
def extract_json(text: str):
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(text[start:end])
    except:
        return None
    return None

def clean_sql(sql: str) -> str:
    sql = sql.strip()
    sql = sql.replace("```sql", "").replace("```", "")

    replacements = {
        "sales_date": "date",
        "quantity_received": "received_stock",
        "profit_amount": "profit",
        "total_profit": "profit"
    }

    for wrong, correct in replacements.items():
        sql = sql.replace(wrong, correct)

    # Force correct source for closing stock
    if "closing_stock" in sql.lower():
        if "vw_fuel_stock" not in sql.lower():
            sql = sql.replace("fuel_stock", "vw_fuel_stock")
    
    # Remove DATE_FORMAT (%Y breaks PyMySQL)
    if "date_format" in sql.lower():
        sql = sql.replace("DATE_FORMAT(date, '%Y-%m')", "date")

    return sql.strip()

def is_safe_sql(sql: str) -> bool:
    forbidden = ["update", "delete", "drop", "insert", "alter", "truncate"]
    return not any(word in sql.lower() for word in forbidden)

def is_data_question(text: str) -> bool:
    keywords = [
        "how much", "profit", "sales", "stock",
        "received", "opening", "closing",
        "trend", "show", "total"
    ]
    return any(k in text.lower() for k in keywords)

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Ask about sales, stock, profit, trends or say hi...")

if user_input:
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # ---------------- GENERAL CHAT ----------------
    if not is_data_question(user_input):
        response = model.generate_content(user_input)
        reply = response.text

        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ---------------- DATA QUESTION ----------------
    else:
        system_prompt = f"""
You are a SQL generator for a petrol bunk system.

CRITICAL RULES:
- Opening stock → fuel_stock.opening_stock
- Closing stock → vw_fuel_stock.closing_stock ONLY
- Fuel received → fuel_stock.received_stock
- Profit column → profit
- Date column → date

Allowed tables:
fuel_sales
fuel_stock
fuel_price
expenses
vw_fuel_sales
vw_fuel_stock
vw_profit_analysis

Rules:
- Generate ONLY SELECT queries
- Do NOT use DATE_FORMAT
- Do NOT guess column names
- Do NOT use UPDATE, DELETE, INSERT, DROP

If a chart is requested, return JSON:
{{
  "sql": "...",
  "chart": "line/bar",
  "x": "column",
  "y": "column"
}}

User question:
{user_input}
"""

        response = model.generate_content(system_prompt)
        content = response.text.strip()

        meta = extract_json(content)

        # ---------------- CHART RESPONSE ----------------
        if meta:
            cleaned_sql = clean_sql(meta["sql"])

            if not is_safe_sql(cleaned_sql):
                st.error("❌ Unsafe SQL detected.")
            else:
                df = pd.read_sql(cleaned_sql, engine)

                with st.chat_message("assistant"):
                    st.dataframe(df, use_container_width=True)

                    if meta["chart"] == "line":
                        st.line_chart(df.set_index(meta["x"])[meta["y"]])
                    elif meta["chart"] == "bar":
                        st.bar_chart(df.set_index(meta["x"])[meta["y"]])

        # ---------------- NUMERIC RESPONSE ----------------
        else:
            cleaned_sql = clean_sql(content)

            if not is_safe_sql(cleaned_sql):
                st.error("❌ Unsafe SQL detected.")
            else:
                df = pd.read_sql(cleaned_sql, engine)
                value = df.iloc[0, 0] if not df.empty else 0

                reply = f"📊 **Result:** {value}"

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": reply}
                )
                with st.chat_message("assistant"):
                    st.markdown(reply)

