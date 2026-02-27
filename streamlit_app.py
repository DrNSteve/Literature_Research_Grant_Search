import streamlit as st
import pandas as pd
from duckduckgo_search import DDGS

# --- CONFIGURATION ---
PAGE_TITLE = "DHA Innovation Portal"
st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon="🏥")

# --- CUSTOM CSS (To look more like your HTML prototype) ---
st.markdown("""
<style>
    .dashboard-header {
        font-size: 2.5rem;
        color: #1f2937;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .dashboard-sub {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #e5e7eb;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #3b82f6;
    }
    .result-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #f97316; /* Elsevier Orange */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .ai-box {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def search_literature(query, max_results=5):
    """Simplified search to bypass DDG bot blocks"""
    # Instead of strict OR blocks, we use natural language weighting + PubMed
    full_query = f"{query} military nursing site:pubmed.ncbi.nlm.nih.gov"
    
    try:
        # Using a slight delay/different initialization can help with rate limits
        results = DDGS().text(full_query, max_results=max_results)
        return list(results) if results else []
    except Exception as e:
        return []

def get_ai_summary(query, search_results):
    if not search_results:
        return None
    context = "\n".join([f"- {r['title']}: {r['body']}" for r in search_results[:3]])
    prompt = f"User asks: {query}. Summarize these 3 search results in 2 short bullet points: {context}"
    try:
        return DDGS().chat(prompt, model="llama-3.1-70b")
    except Exception:
        return "AI Summary currently unavailable due to server load."

# --- MAIN APP LAYOUT ---

st.markdown('<div class="dashboard-header">Feedback Analytics & Search</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-sub">Visualizing front-line insights to drive meaningful change.</div>', unsafe_allow_html=True)

# Metrics Row (Mimicking your HTML dashboard)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><div style="color:#6b7280; font-weight:600;">Trusted Sources</div><div class="metric-value">4+</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><div style="color:#6b7280; font-weight:600;">Active Projects</div><div class="metric-value">73</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><div style="color:#6b7280; font-weight:600;">Implemented Solutions</div><div class="metric-value" style="color:#10b981;">15</div></div>', unsafe_allow_html=True)

st.write("---")

tab1, tab2 = st.tabs(["🔎 Evidence Search", "📝 Submit Feedback"])

# --- TAB 1: SEARCH ---
with tab1:
    st.markdown("### Search Literature & Grants")
    
    col_a, col_b = st.columns([4, 1])
    with col_a:
        query = st.text_input("Search keywords", placeholder="e.g. Military Readiness APRN", label_visibility="collapsed")
    with col_b:
        search_btn = st.button("Search Pure & PubMed", type="primary", use_container_width=True)
    
    if search_btn and query:
        with st.spinner("Scanning databases..."):
            results = search_literature(query)
            
            if results:
                summary = get_ai_summary(query, results)
                if summary:
                    st.markdown(f"""
                    <div class="ai-box">
                        <strong style="color:#166534;">🤖 AI Synthesis:</strong><br>
                        <span style="color:#14532d;">{summary}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("#### Live Expert & Literature Matching")
                for res in results:
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
                st.error("No results found. The search engine might be temporarily blocking automated queries. Please try a different keyword like 'burnout'.")

# --- TAB 2: SUBMISSION ---
with tab2:
    st.markdown("### Route Feedback to Leadership")
    st.info("To maintain OPSEC and secure data handling, all feedback is routed through official channels.")
    survey_url = "https://www.milsuite.mil" 
    st.markdown(f'''<br><a href="{survey_url}" target="_blank" style="background-color: #1E3A8A; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">🚀 Launch Secure Survey (CAC Required)</a>''', unsafe_allow_html=True)
