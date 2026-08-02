import streamlit as st
import pandas as pd
from groq import Groq

# --- Page Setup ---
st.set_page_config(page_title="Careem Food: Decision Brief Generator", layout="wide")

# --- Connect the Groq AI Brain ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception:
    st.error("API Key not found. Please add your GROQ_API_KEY to Streamlit Secrets.")

# --- Website Header ---
st.title("📊 Decision Brief Generator")
st.markdown("Automated plan-vs-actual translation for weekly growth reviews.")

# --- Sidebar / CSV Upload Section ---
st.sidebar.header("📁 Data Input Options")
st.sidebar.write("Upload your own weekly KPI CSV or use the default Dubai market dataset.")

uploaded_file = st.sidebar.file_uploader("Upload Weekly KPI CSV", type=["csv"])

# --- Default Dummy Data ---
default_data = {
    "Metric": ["MAU", "Orders", "Conversion Rate (%)", "Retention (%)", "ARPU ($)", "OPU", "CAC ($)", "Promo Spend ($)", "Gross Revenue ($)"],
    "Plan": [450000, 1575000, 18.0, 45.0, 85.00, 3.5, 15.00, 120000, 38250000],
    "Actual": [465000, 1441500, 13.8, 46.8, 81.50, 3.1, 18.50, 145000, 35702500],
    "Prior_Week": [440000, 1500000, 17.5, 44.5, 84.00, 3.4, 14.50, 115000, 36960000]
}

# Load either uploaded CSV or default data
if uploaded_file is not None:
    try:
        df_input = pd.read_csv(uploaded_file)
        st.sidebar.success("Custom CSV loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")
        df_input = pd.DataFrame(default_data)
else:
    df_input = pd.DataFrame(default_data)

# --- Display and Edit Data Table ---
st.subheader("1. Weekly Performance Data")
st.write("Review or edit the active dataset below before generating the brief:")
edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)

# --- The Math (Calculating variances if columns exist) ---
def calculate_variances(df):
    try:
        if 'Actual' in df.columns and 'Plan' in df.columns:
            df['Delta_vs_Plan (%)'] = ((df['Actual'] - df['Plan']) / df['Plan'] * 100).round(1)
        if 'Actual' in df.columns and 'Prior_Week' in df.columns:
            df['WoW_Trend (%)'] = ((df['Actual'] - df['Prior_Week']) / df['Prior_Week'] * 100).round(1)
    except Exception:
        pass
    return df

processed_df = calculate_variances(edited_df)

# --- The Generate Button ---
if st.button("Generate Executive Decision Brief 🚀", type="primary"):
    
    with st.spinner("Analyzing variances and drafting executive brief using Llama 3..."):
        
        data_string = processed_df.to_markdown()
        
        prompt = f"""
        Act as a Senior Growth Manager for Careem Food. Review the following weekly KPI data:
        
        {data_string}
        
        Write a concise, executive-ready decision brief analyzing this performance. 
        Do not explain your math. Keep it highly operational and urgent. 
        
        Format strictly using these headings:
        
        ### 📉 What Changed
        (1-2 sentences summarizing top-line performance vs plan)
        
        ### 🔍 Primary Drivers
        (Bullet points identifying the top 3 drivers of revenue/volume variance)
        
        ### ⚡ Recommended Actions
        (3 specific, actionable steps for the commercial/growth team to take next week to correct negative variances)
        
        ### ⚠️ Risks to Monitor
        (1-2 risks for the upcoming week based on the WoW trends)
        """
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            st.divider()
            st.subheader("2. Executive Decision Brief")
            st.markdown(chat_completion.choices[0].message.content)
            st.success("Brief generated successfully via Groq! Ready for commercial review.")
            
        except Exception as e:
            st.error(f"Groq API Error: {e}")
