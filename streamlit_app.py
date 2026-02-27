import streamlit as st
import pandas as pd
from duckduckgo_search import DDGS
import urllib.parse

# --- CONFIGURATION ---
PAGE_TITLE = "Front-Line Innovation Portal"
SEARCH_DOMAINS = [
    "triservicenurse.org",
    "usuhs.edu",
    "health.mil",
    "pubmed.ncbi.nlm.nih.gov"
]

st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon="🏥")

# --- CSS STYLING ---
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-text {
        text-align: center;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s;
    }
    .result-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .ai-summary {
        background-color: #EFF6FF; /* Light Blue */
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 2rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def search_whitelist(query, max_results=8):
    """Searches specific domains using DuckDuckGo."""
    site_string = " OR ".join([f"site:{domain}" for domain in SEARCH_DOMAINS])
    full_query = f"({site_string}) {query}"
    
    try:
        results = DDGS().text(full_query, max_results=max_results)
        return list(results) if results else []
    except Exception as e:
        st.error(f"Search connectivity issue: {e}")
        return []

def get_ai_summary(query, search_results):
    """Uses DuckDuckGo's Chat feature to synthesize results."""
    if not search_results:
        return None
    
    context = "\n".join([f"- {r['title']}: {r['body']}" for r in search_results[:4]])
    prompt = f"""
    You are a helpful research assistant for military nursing.
    User Question: "{query}"
    
    Based on the following search result snippets, provide a 3-bullet point summary of the key findings or resources.
    
    Context:
    {context}
    """
    
    try:
        response = DDGS().chat(prompt, model="llama-3.1-70b")
        return response
    except Exception:
        return "Unable to generate AI synthesis at this time (rate limit). Please review the search results below directly."

# --- MAIN APP LAYOUT ---

st.markdown(f'<div class="main-header">{PAGE_TITLE}</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Search approved funding databases & resources.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔎 Evidence Search", "📝 Submit Feedback"])

# --- TAB 1: SEARCH ---
with tab1:
    st.info(f"Searching trusted domains: {', '.join(SEARCH_DOMAINS)}")
    
    col_a, col_b = st.columns([4, 1])
    with col_a:
        query = st.text_input("Search keywords", placeholder="e.g. TBI Care, Sleep Hygiene, Burnout prevention", label_visibility="collapsed")
    with col_b:
        search_btn = st.button("Find Resources", type="primary", use_container_width=True)
    
    if search_btn and query:
        with st.spinner("Scanning databases..."):
            results = search_whitelist(query)
            
            if results:
                summary = get_ai_summary(query, results)
                if summary:
                    st.markdown(f"""
                    <div class="ai-summary">
                        <strong>🤖 AI Synthesis (Beta):</strong><br>
                        {summary}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.subheader(f"Found {len(results)} Resources")
                for res in results:
                    with st.container():
                        st.markdown(f"""
                        <div class="result-card">
                            <a href="{res['href']}" target="_blank" style="text-decoration:none; color:#1E3A8A; font-weight:bold; font-size:1.1rem;">
                                {res['title']}
                            </a>
                            <div style="color:#059669; font-size:0.8rem; margin-top:4px;">{res['href'][:60]}...</div>
                            <div style="color:#4B5563; margin-top:8px;">{res['body']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No results found. Try using simpler keywords.")

# --- TAB 2: SUBMISSION ---
with tab2:
    st.markdown("### Submit Your Insight")
    st.markdown("""
    We use **milSurvey** (or approved survey tools) to ensure your data is collected securely and aggregated for leadership review.
    
    Please click the button below to access the secure submission form.
    """)
    
    survey_url = "https://www.milsuite.mil" 
    
    st.markdown(f'''
        <a href="{survey_url}" target="_blank" style="
            display: inline-block;
            background-color: #1E3A8A;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 1.1rem;
            margin-top: 10px;">
            🚀 Launch Secure Survey
        </a>
    ''', unsafe_allow_html=True)
    
    st.caption("Note: CAC authentication may be required for the survey tool.")

# --- SIDEBAR INFO ---
with st.sidebar:
    st.header("About")
    st.markdown("""
    **Version:** Beta 1.1 (Search Focus)
    
    **Privacy Notice:** - Search queries are processed anonymously via DuckDuckGo.
    - No survey data is stored on this website's server.
    """)
    st.divider()
    st.info("Developed for DHA Nursing Research Demo.")
