import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
 
st.set_page_config(page_title="Data Analyst Agent", page_icon="📊", layout="wide")
 
st.title("📊 Data Analyst Agent")
st.write("Upload your CSV or Excel file — I'll analyze it, make charts, and answer your questions!")
 
# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")
st.sidebar.caption("Get your FREE API key at console.groq.com")
st.sidebar.markdown("---")
st.sidebar.markdown("**How to use:**")
st.sidebar.markdown("1. Get free key from console.groq.com")
st.sidebar.markdown("2. Upload your CSV or Excel file")
st.sidebar.markdown("3. Click Generate Insights")
st.sidebar.markdown("4. Ask questions about your data!")
 
# --- File Upload ---
uploaded_file = st.file_uploader("📂 Upload your file here", type=["csv", "xlsx"])
 
if uploaded_file is not None:
 
    # Load the file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
 
    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
 
    # --- Section 1: Data Preview ---
    st.markdown("---")
    st.subheader("📋 Data Preview")
    st.dataframe(df, use_container_width=True)
 
    # --- Section 2: Quick Stats ---
    st.markdown("---")
    st.subheader("📌 Quick Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Missing Values", int(df.isnull().sum().sum()))
    col4.metric("Numeric Columns", len(df.select_dtypes(include='number').columns))
 
    # --- Section 3: Column Info ---
    st.markdown("---")
    st.subheader("🔍 Column Details")
    col_info = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.values,
        "Missing Values": df.isnull().sum().values,
        "Unique Values": df.nunique().values
    })
    st.dataframe(col_info, use_container_width=True)
 
    # --- Section 4: Charts ---
    st.markdown("---")
    st.subheader("📈 Auto Charts")
 
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
 
    if len(numeric_cols) >= 1:
        tab1, tab2, tab3 = st.tabs(["Distribution", "Correlation Heatmap", "Bar Chart"])
 
        with tab1:
            selected_col = st.selectbox("Select a column to visualize", numeric_cols)
            fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}",
                               color_discrete_sequence=["#7F77DD"])
            st.plotly_chart(fig, use_container_width=True)
 
        with tab2:
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr()
                fig2 = px.imshow(corr, text_auto=True, title="Correlation Heatmap",
                                 color_continuous_scale="RdBu_r")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Need at least 2 numeric columns for a heatmap.")
 
        with tab3:
            x_col = st.selectbox("Select X axis", df.columns.tolist(), key="bar_x")
            y_col = st.selectbox("Select Y axis", numeric_cols, key="bar_y")
            fig3 = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}",
                          color_discrete_sequence=["#1D9E75"])
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No numeric columns found for charts.")
 
    # --- Helper: build data summary for LLM ---
    def build_summary(df):
        return f"""
Dataset has {df.shape[0]} rows and {df.shape[1]} columns.
Column names and types: {dict(df.dtypes.astype(str))}.
Missing values per column: {df.isnull().sum().to_dict()}.
Basic statistics:
{df.describe().to_string()}
First 5 rows sample:
{df.head(5).to_string()}
"""
 
    # --- Helper: call Groq ---
    def ask_groq(api_key, prompt):
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
 
    # --- Section 5: AI Insights ---
    st.markdown("---")
    st.subheader("🤖 AI-Powered Insights")
 
    if not api_key:
        st.warning("Please enter your Groq API key in the sidebar to get AI insights.")
    else:
        if st.button("✨ Generate Insights"):
            with st.spinner("AI is analyzing your data..."):
                summary = build_summary(df)
                prompt = f"""You are a friendly data analyst. 
Analyze this dataset and give exactly 5 key insights in simple, plain English. 
Mention specific column names and numbers. 
Format each insight as a numbered point starting with an emoji.
 
Dataset summary:
{summary}"""
                result = ask_groq(api_key, prompt)
                st.markdown(result)
 
        # --- Section 6: Q&A ---
        st.markdown("---")
        st.subheader("💬 Ask a Question About Your Data")
        st.caption("Examples: Which column has the most missing values? What is the average of column X?")
 
        user_question = st.text_input("Type your question here...")
 
        if user_question:
            with st.spinner("Thinking..."):
                summary = build_summary(df)
                prompt = f"""You are a helpful data analyst.
Answer this question about the dataset in simple, clear language.
Be specific and mention numbers where possible.
 
Question: {user_question}
 
Dataset summary:
{summary}"""
                answer = ask_groq(api_key, prompt)
                st.markdown(answer)
 
else:
    st.info("👆 Upload a CSV or Excel file above to get started.")
    st.markdown("---")
    st.markdown("### What this app can do:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("📋 **Preview your data**\nSee all rows and columns clearly")
    with col2:
        st.markdown("📈 **Auto charts**\nHistogram, heatmap, bar chart")
    with col3:
        st.markdown("🤖 **AI insights**\nAsk questions in plain English")
 
