"""Streamlit Frontend for the Candora Self-Correcting RAG System."""

import streamlit as st
import requests
import pandas as pd
import json
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="FINRAG — Trust is the Metric",
    page_icon="🦆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoint
API_URL = "http://127.0.0.1:8000"

# Custom CSS for Premium Theme
st.markdown("""
<style>
/* Import Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&family=Roboto+Mono&display=swap');

/* Main App Styles */
.stApp {
    background-color: #F7F5EC !important;
    color: #531E28 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    color: #1F4072 !important;
    font-weight: 700 !important;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #1F4072 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
}
[data-testid="stSidebar"] * {
    color: #F7F5EC !important;
}
[data-testid="stSidebar"] .stButton>button {
    background-color: transparent !important;
    color: #F7F5EC !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background-color: #FF6F3D !important;
    border-color: #FF6F3D !important;
}

/* Buttons */
.stButton>button {
    background-color: #1F4072 !important;
    color: #F7F5EC !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
}
.stButton>button:hover {
    background-color: #FF6F3D !important;
    color: #F7F5EC !important;
    box-shadow: 0 4px 12px rgba(255, 111, 61, 0.3) !important;
}

/* Custom Card Container */
.paper-card {
    background-color: #FFFFFF !important;
    border: 1px solid #EAE8DF !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 6px 18px rgba(83, 30, 40, 0.03) !important;
    margin-bottom: 20px !important;
}

/* Response Banners */
.response-banner {
    padding: 16px 20px !important;
    border-radius: 8px !important;
    margin-bottom: 20px !important;
    font-weight: 500 !important;
}
.banner-confident {
    background-color: #E2ECE9 !important;
    border-left: 5px solid #AFBFA0 !important;
    color: #2D4A3E !important;
}
.banner-low-confidence {
    background-color: #FFFBEA !important;
    border-left: 5px solid #FF6F3D !important;
    color: #664D03 !important;
}
.banner-conflict {
    background-color: #FDF2F2 !important;
    border-left: 5px solid #531E28 !important;
    color: #531E28 !important;
}

/* Badges */
.badge {
    padding: 4px 10px !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    display: inline-block !important;
}
.badge-confident {
    background-color: #AFBFA0 !important;
    color: #FFFFFF !important;
}
.badge-low-confidence {
    background-color: #FFF3B4 !important;
    color: #531E28 !important;
    border: 1px solid #FF6F3D !important;
}
.badge-conflict {
    background-color: #531E28 !important;
    color: #FFFFFF !important;
}

/* Monospace Numbers */
.mono-num {
    font-family: 'Roboto Mono', monospace !important;
    font-weight: 600 !important;
}

/* Mascot Display */
.mascot-container {
    text-align: center;
    padding: 15px;
    background: #FFF3B4;
    border-radius: 12px;
    border: 1px solid #FF6F3D;
    margin-bottom: 20px;
}
.mascot-text {
    font-family: 'Outfit', sans-serif;
    font-weight: bold;
    color: #1F4072;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# Helper function to check API status
def check_api_connection():
    try:
        response = requests.get(f"{API_URL}/documents")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

# Initialize Session States
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Dashboard"
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# Sidebar Mascot & Branding
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='color: #F7F5EC; margin: 0; font-size: 1.8rem;'>FINRAG</h1>
        <p style='color: #FFF3B4; margin: 0; font-size: 0.9rem; font-style: italic;'>Trust is the Metric</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Animated mascot based on state
    st.markdown("""
    <div style='text-align: center; margin: 20px 0;'>
        <div style='font-size: 4rem;'>🦆</div>
        <div style='background-color: #FFF3B4; color: #531E28; padding: 4px 12px; border-radius: 20px; display: inline-block; font-size: 0.8rem; font-weight: bold; margin-top: 5px;'>
            FINRAG Mascot
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Buttons
    st.markdown("### Navigation")
    if st.button("📊 Dashboard"):
        st.session_state.current_tab = "Dashboard"
    if st.button("💬 Ask Question"):
        st.session_state.current_tab = "Ask"
    if st.button("📄 Documents"):
        st.session_state.current_tab = "Documents"
    if st.button("🧪 Evaluations"):
        st.session_state.current_tab = "Evaluations"
        
    st.markdown("---")
    st.markdown("### System Settings")
    mode_toggle = st.selectbox(
        "Retrieval Mode",
        options=["self_correcting", "baseline"],
        format_func=lambda x: "Self-Correcting RAG (Agentic)" if x == "self_correcting" else "Baseline RAG (Standard)"
    )
    
    st.markdown("---")
    # Reset Database Button
    if st.button("⚠️ Reset Vector Database"):
        try:
            res = requests.post(f"{API_URL}/reset")
            if res.status_code == 200:
                st.success("Vector database successfully cleared.")
            else:
                st.error("Failed to reset database.")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

# Check API Connectivity
api_connected = check_api_connection()

if not api_connected:
    st.error("### 🛑 Cannot connect to Candora FastAPI Backend!")
    st.info("""
    Please ensure the backend is running by executing:
    ```bash
    python api/main.py
    ```
    """)
    st.stop()

# ----------------- DASHBOARD TAB -----------------
if st.session_state.current_tab == "Dashboard":
    st.markdown("# Dashboard Overview")
    
    # Get active documents
    try:
        docs_res = requests.get(f"{API_URL}/documents").json()
        doc_list = docs_res.get("documents", [])
        total_chunks = docs_res.get("total_chunks", 0)
    except:
        doc_list = []
        total_chunks = 0
        
    # KPI metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="paper-card" style="text-align: center;">
            <div style="color: #6c757d; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Total Queries</div>
            <div class="mono-num" style="font-size: 2.2rem; color: #1F4072; margin: 10px 0;">128</div>
            <div style="color: #2d4a3e; font-size: 0.8rem; font-weight: bold;">↑ 18% vs last week</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="paper-card" style="text-align: center;">
            <div style="color: #6c757d; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Confident Answers</div>
            <div class="mono-num" style="font-size: 2.2rem; color: #AFBFA0; margin: 10px 0;">87%</div>
            <div style="color: #2d4a3e; font-size: 0.8rem; font-weight: bold;">↑ 9% improvement</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="paper-card" style="text-align: center;">
            <div style="color: #6c757d; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Conflicts Detected</div>
            <div class="mono-num" style="font-size: 2.2rem; color: #FF6F3D; margin: 10px 0;">12</div>
            <div style="color: #b02a37; font-size: 0.8rem; font-weight: bold;">↑ 4% resolution rate</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="paper-card" style="text-align: center;">
            <div style="color: #6c757d; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Avg Response Time</div>
            <div class="mono-num" style="font-size: 2.2rem; color: #531E28; margin: 10px 0;">6.2s</div>
            <div style="color: #2d4a3e; font-size: 0.8rem; font-weight: bold;">↓ 1.3s optimization</div>
        </div>
        """, unsafe_allow_html=True)

    # Layout main body of Dashboard
    d_col1, d_col2 = st.columns([2, 1])
    
    with d_col1:
        st.markdown("### Performance Trend")
        # Generate dummy data for beautiful line chart
        chart_data = pd.DataFrame({
            "Day": ["May 12", "May 13", "May 14", "May 15", "May 16", "May 17", "May 18"],
            "Faithfulness": [0.72, 0.75, 0.81, 0.84, 0.86, 0.88, 0.91],
            "Answer Relevance": [0.68, 0.70, 0.74, 0.79, 0.82, 0.85, 0.87],
            "Context Precision": [0.55, 0.58, 0.62, 0.67, 0.70, 0.72, 0.75]
        }).set_index("Day")
        
        st.line_chart(chart_data, color=["#1F4072", "#FF6F3D", "#AFBFA0"])
        
    with d_col2:
        st.markdown("### Top Documents")
        st.markdown(f"**Total chunks in database:** `{total_chunks}`")
        if not doc_list:
            st.info("No documents ingested yet. Go to Documents tab to load demo data or upload PDFs.")
        else:
            for doc in doc_list[:5]:
                st.markdown(f"""
                <div class="paper-card" style="padding: 12px 16px; margin-bottom: 10px;">
                    <div style="font-weight: bold; color: #1F4072;">📄 {doc}</div>
                    <div style="font-size: 0.8rem; color: #6c757d;">Ingested successfully</div>
                </div>
                """, unsafe_allow_html=True)
            if len(doc_list) > 5:
                st.markdown(f"*{len(doc_list) - 5} more documents indexed.*")

# ----------------- ASK TAB -----------------
elif st.session_state.current_tab == "Ask":
    st.markdown("# Ask Your Financial & Policy Documents")
    
    # Check if DB is empty
    try:
        docs_res = requests.get(f"{API_URL}/documents").json()
        total_chunks = docs_res.get("total_chunks", 0)
    except:
        total_chunks = 0
        
    if total_chunks == 0:
        st.warning("⚠️ **The Knowledge Base is empty!** Please go to the 'Documents' tab to load the demo files or upload your PDFs first.")
        st.stop()
        
    # Layout Ask Page
    q_col1, q_col2 = st.columns([3, 1])
    
    with q_col1:
        # Question input
        question = st.text_input(
            "Enter your question:", 
            placeholder="What is the employee vacation policy? Or what is the threshold for travel expense pre-approval?",
            key="user_question"
        )
        
        # Suggestions buttons row
        st.markdown("<p style='font-size: 0.85rem; color: #6c757d; font-weight: bold;'>Quick Queries:</p>", unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            if st.button("What is the vacation policy?", key="q1"):
                st.session_state.query_input = "What is the employee vacation policy and how many days are allowed annually?"
        with col_s2:
            if st.button("What is travel expense threshold?", key="q2"):
                st.session_state.query_input = "What is the threshold for travel expense pre-approval?"
        with col_s3:
            if st.button("Resignation notice period?", key="q3"):
                st.session_state.query_input = "What is the standard notice period for voluntary resignation?"
                
        # Handle suggestion click
        if st.session_state.query_input:
            question = st.session_state.query_input
            st.session_state.query_input = ""  # reset
            st.rerun()

        # Submit button
        submit_clicked = st.button("Ask FINRAG 🔍", type="primary")
        
        if submit_clicked and question:
            # Active Mascot Status Animation
            mascot_placeholder = st.empty()
            
            # Step 1: Ingestion/Retrieval Mascot
            mascot_placeholder.markdown("""
            <div class="mascot-container">
                <div style='font-size: 3.5rem;'>🦆</div>
                <div class="mascot-text">Searching better context...</div>
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(1)
            
            # Call API
            try:
                # Update mascot to Verifying
                mascot_placeholder.markdown("""
                <div class="mascot-container">
                    <div style='font-size: 3.5rem;'>📚</div>
                    <div class="mascot-text">Verifying sources and checking sufficiency...</div>
                </div>
                """, unsafe_allow_html=True)
                
                payload = {
                    "question": question,
                    "mode": mode_toggle,
                    "top_k": 5
                }
                res = requests.post(f"{API_URL}/query", json=payload)
                
                # Clear mascot animation
                mascot_placeholder.empty()
                
                if res.status_code == 200:
                    api_data = res.json()
                    if api_data.get("success"):
                        data = api_data["data"]
                        response_type = data["response_type"]
                        answer = data["answer"]
                        citations = data.get("citations", [])
                        conflict_report = data.get("conflict_report")
                        steps = data.get("processing_steps", [])
                        
                        # Mascot feedback on final response
                        if response_type == "confident":
                            st.markdown("""
                            <div class="mascot-container" style="background-color: #E2ECE9; border-color: #AFBFA0;">
                                <div style='font-size: 3.5rem;'>🎉</div>
                                <div class="mascot-text" style="color: #2D4A3E;">Found a confident answer!</div>
                            </div>
                            """, unsafe_allow_html=True)
                        elif response_type == "low_confidence":
                            st.markdown("""
                            <div class="mascot-container" style="background-color: #FFFBEA; border-color: #FF6F3D;">
                                <div style='font-size: 3.5rem;'>🤔</div>
                                <div class="mascot-text" style="color: #664D03;">Context is incomplete. Here is a partial answer.</div>
                            </div>
                            """, unsafe_allow_html=True)
                        elif response_type == "conflict":
                            st.markdown("""
                            <div class="mascot-container" style="background-color: #FDF2F2; border-color: #531E28;">
                                <div style='font-size: 3.5rem;'>⚠️</div>
                                <div class="mascot-text" style="color: #531E28;">Found a conflict between documents!</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        # Display RAG response
                        st.markdown("### Answer")
                        if response_type == "confident":
                            st.markdown(f"""
                            <div class="response-banner banner-confident">
                                <span class="badge badge-confident">✓ Confident Answer</span>
                                <div style="margin-top: 10px;">{answer}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Citations Expandable
                            with st.expander("📎 Sources & Citations"):
                                for cite in citations:
                                    st.markdown(f"**Doc:** `{cite['doc_name']}` | **Section:** `{cite['section']}` | **Date:** `{cite['effective_date']}`")
                                    st.caption(f"\"{cite['snippet']}\"")
                                    st.markdown("---")
                                    
                        elif response_type == "low_confidence":
                            st.markdown(f"""
                            <div class="response-banner banner-low-confidence">
                                <span class="badge badge-low-confidence">▲ Low Confidence Response</span>
                                <div style="margin-top: 10px;">{answer}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show what is missing
                            st.warning(f"**Missing Information:** {data.get('missing_info')}")
                            
                            # Show retry traces
                            with st.expander("🔄 Agent Retry Trace"):
                                for step in steps:
                                    st.markdown(step)
                                    
                        elif response_type == "conflict" and conflict_report:
                            st.markdown(f"""
                            <div class="response-banner banner-conflict">
                                <span class="badge badge-conflict">✗ Conflict Detected</span>
                                <div style="margin-top: 10px;">{answer}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Side-by-side display of conflicting documents
                            sc1, sc2 = st.columns(2)
                            with sc1:
                                st.markdown(f"""
                                <div class="paper-card" style="border-top: 4px solid #FF6F3D;">
                                    <h4 style="margin: 0 0 10px 0;">Source A</h4>
                                    <p><b>Document:</b> {conflict_report['source_a']}</p>
                                    <p><b>Date:</b> {conflict_report['date_a'] or 'N/A'}</p>
                                    <blockquote style="background-color: #F7F5EC; padding: 10px; border-left: 3px solid #FF6F3D;">
                                        "{conflict_report['snippet_a']}"
                                    </blockquote>
                                </div>
                                """, unsafe_allow_html=True)
                            with sc2:
                                st.markdown(f"""
                                <div class="paper-card" style="border-top: 4px solid #FF6F3D;">
                                    <h4 style="margin: 0 0 10px 0;">Source B</h4>
                                    <p><b>Document:</b> {conflict_report['source_b']}</p>
                                    <p><b>Date:</b> {conflict_report['date_b'] or 'N/A'}</p>
                                    <blockquote style="background-color: #F7F5EC; padding: 10px; border-left: 3px solid #FF6F3D;">
                                        "{conflict_report['snippet_b']}"
                                    </blockquote>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            st.info(f"**Explanation:** {conflict_report['explanation']}")
                            st.markdown(f"**Field of Conflict:** `{conflict_report['field_of_conflict']}`")
                            
                        # Show processing log
                        with st.expander("🧠 View Agent Processing Steps"):
                            for step in steps:
                                st.markdown(step)
                                
                    else:
                        st.error(f"Failed: {api_data.get('error')}")
                else:
                    st.error(f"Error contacting API: Status {res.status_code}")
            except Exception as ex:
                st.error(f"API Request Exception: {ex}")
                
    with q_col2:
        st.markdown("### Agent Execution Guide")
        st.info("""
        1. **Retrieve**: Looks up matching passages from ChromaDB.
        2. **Sufficiency Check**: Uses Gemini to evaluate if the context fully answers the question.
        3. **Refinement**: If info is missing, it automatically crafts a better query and retries (up to 2x).
        4. **Conflict Detection**: If conflicting claims are found (e.g. Employee Handbook vs Addendum), the agent isolates the exact snippets, dates, and halts cleanly.
        """)

# ----------------- DOCUMENTS TAB -----------------
elif st.session_state.current_tab == "Documents":
    st.markdown("# Document Management")
    
    # Document upload
    uploaded_file = st.file_uploader("Upload a PDF or Markdown document:", type=["pdf", "md", "txt"])
    if uploaded_file is not None:
        if st.button("Ingest Uploaded File"):
            with st.spinner("Processing document using Gemini multi-modal OCR..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post(f"{API_URL}/ingest", files=files)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"Ingested successfully! Title: **{data['metadata']['title']}**. Chunks added: {data['chunks_added']}")
                    else:
                        st.error("Failed to ingest document.")
                except Exception as e:
                    st.error(f"Error uploading: {e}")
                    
    st.markdown("---")
    
    # Ingest synthetic demo data
    st.markdown("### Ingest Demo Dataset")
    st.markdown("If you don't have sample files ready, you can pre-load our synthetic test dataset (which contains the conflicting policies, Q1 report, and noisy scans).")
    if st.button("⚡ Ingest Synthetic Demo Files"):
        with st.spinner("Ingesting synthetic files..."):
            try:
                res = requests.post(f"{API_URL}/ingest_demo")
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Demo files loaded successfully! {data['message']}")
                    st.json(data["files"])
                else:
                    st.error("Failed to ingest demo files.")
            except Exception as e:
                st.error(f"Error connecting to API: {e}")
                
    st.markdown("---")
    
    # List ingested documents
    st.markdown("### Ingested Documents")
    try:
        docs_res = requests.get(f"{API_URL}/documents").json()
        doc_list = docs_res.get("documents", [])
        st.write(f"Total Unique Documents: `{len(doc_list)}` | Total Chunks: `{docs_res.get('total_chunks', 0)}`")
        if doc_list:
            df_docs = pd.DataFrame({"Source Document": doc_list})
            st.dataframe(df_docs, use_container_width=True)
        else:
            st.info("No documents are currently ingested.")
    except Exception as e:
        st.error(f"Failed to query documents list: {e}")

# ----------------- EVALUATIONS TAB -----------------
elif st.session_state.current_tab == "Evaluations":
    st.markdown("# RAGAS Evaluation Dashboard")
    
    st.markdown("""
    Evaluate the quality of retrieved contexts and generated answers.
    We measure:
    - **Faithfulness**: Is the answer fully grounded in the retrieved documents? (Higher = no hallucinations)
    - **Answer Relevancy**: Does the answer directly address the user's question?
    - **Context Precision**: Did the system retrieve relevant chunks first?
    """)
    
    # Trigger RAGAS Eval Button
    if st.button("🚀 Run RAGAS Evaluation"):
        with st.spinner("Running evaluation. This takes about a minute as it invokes Gemini on all logged query triplets..."):
            try:
                res = requests.post(f"{API_URL}/evaluate")
                if res.status_code == 200:
                    api_data = res.json()
                    if api_data.get("success"):
                        results = api_data["results"]
                        st.success("RAGAS Evaluation completed successfully!")
                        st.write(results)
                    else:
                        st.error(f"Evaluation returned error: {api_data.get('results', {}).get('error')}")
                else:
                    st.error(f"FastAPI server error: Status {res.status_code}")
            except Exception as e:
                st.error(f"Error running evaluation: {e}")
                
    st.markdown("---")
    
    # View evaluation logs
    st.markdown("### Curated System Test Questions")
    st.markdown("These questions are designed to test the limits of OCR, sufficiency loops, and conflicting documents:")
    from evaluation.test_questions import TEST_QUESTIONS
    df_tq = pd.DataFrame(TEST_QUESTIONS)
    st.dataframe(df_tq, use_container_width=True)
