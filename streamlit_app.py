import streamlit as st
import pandas as pd
import requests

# --- CONFIGURATION ---
PAGE_TITLE = "DHA Innovation Portal"
st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon="🏥")

# --- CUSTOM CSS ---
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

# --- HELPER FUNCTIONS (PUBMED API) ---

def search_pubmed(query, max_results=5):
    """Uses the official, free US Gov PubMed API to fetch real literature."""
    try:
        # Step 1: Search for article IDs
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax={max_results}"
        res = requests.get(search_url).json()
        id_list = res.get('esearchresult', {}).get('idlist', [])
        
        if not id_list:
            return []

        # Step 2: Fetch article details using the IDs
        ids = ",".join(id_list)
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids}&retmode=json"
        sum_res = requests.get(summary_url).json()
        
        results = []
        for uid in id_list:
            data = sum_res.get('result', {}).get(uid, {})
            title = data.get('title', 'No Title Available')
            source = data.get('source', 'Unknown Journal')
            pubdate = data.get('pubdate', 'Unknown Date')
            authors = ", ".join([a.get('name', '') for a in data.get('authors', [])[:3]])
            if len(data.get('authors', [])) > 3:
                authors += " et al."
                
            results.append({
                'title': title,
                'href': f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                'body': f"**{source}** ({pubdate}) | Authors: {authors}"
            })
        return results
    except Exception as e:
        return []

def get_demo_summary(query):
    """Provides a guaranteed, stable AI synthesis for demo purposes."""
    query_lower = query.lower()
    if "readiness" in query_lower or "aprn" in query_lower:
        return """Based on the literature, APRN operational readiness is a critical focus area. Key themes include: 
        <br>• The need for standardized clinical competency assessments pre-deployment. 
        <br>• Identification of training gaps in austere trauma and critical care stabilization. 
        <br>• The integration of DNP education directly with military operational requirements."""
    elif "burnout" in query_lower or "moral" in query_lower:
        return """Current evidence on military nursing burnout indicates:
        <br>• High correlation between administrative burden (EHR charting) and staff turnover.
        <br>• Deployment tempo and moral injury significantly impact long-term retention.
        <br>• Interventions focusing on unit-level leadership support show the highest efficacy."""
    else:
        return """<em>Prototype Note:</em> AI Synthesis is in Demo Mode. In production, this module will plug directly into an IL5-authorized LLM (like Ask Sage) to synthesize the literature pulled below."""

# --- MAIN APP LAYOUT ---

st.markdown('<div class="dashboard-header">Feedback Analytics & Search</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-sub">Visualizing front-line insights to drive meaningful change.</div>', unsafe_allow_html=True)

# Metrics Row 
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><div style="color:#6b7280; font-weight:600;">Trusted Sources</div><div class="metric-value">PubMed API</div></div>', unsafe_allow_html=True)
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
        query = st.text_input("Search keywords", placeholder="e.g. Military Readiness APRN, Burnout", label_visibility="collapsed")
    with col_b:
        search_btn = st.button("Search PubMed", type="primary", use_container_width=True)
    
    if search_btn and query:
        with st.spinner("Querying National Library of Medicine (PubMed)..."):
            results = search_pubmed(query)
            
            if results:
                # Demo AI Summary
                summary = get_demo_summary(query)
                st.markdown(f"""
                <div class="ai-box">
                    <strong style="color:#166534;">🤖 AI Synthesis (Prototype Mode):</strong><br>
                    <span style="color:#14532d;">{summary}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Live Literature Matching")
                for res in results:
                    st.markdown(f"""
                    <div class="result-card">
                        <a href="{res['href']}" target="_blank" style="text-decoration:none; color:#1E3A8A; font-weight:bold; font-size:1.1rem;">
                            {res['title']}
                        </a>
                        <div style="color:#059669; font-size:0.8rem; margin-top:4px;">{res['href']}</div>
                        <div style="color:#4B5563; margin-top:8px;">{res['body']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("No results found. Please check your spelling or try broader keywords.")

# --- TAB 2: SUBMISSION ---
with tab2:
    st.markdown("### Route Feedback to Leadership")
    st.info("To maintain OPSEC and secure data handling, all feedback is routed through official channels.")
    survey_url = "https://www.milsuite.mil" 
    st.markdown(f'''<br><a href="{survey_url}" target="_blank" style="background-color: #1E3A8A; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">🚀 Launch Secure Survey (CAC Required)</a>''', unsafe_allow_html=True)
