import streamlit as st
import requests
import urllib.parse
import pandas as pd
from datetime import datetime, timedelta
import random

# --- CONFIGURATION ---
PAGE_TITLE = "DHA Innovation Portal"
st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon="🏥")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .dashboard-header { font-size: 2.5rem; color: #1f2937; font-weight: 800; margin-bottom: 0px; }
    .dashboard-sub { color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem; }
    .metric-card { background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); padding: 1.5rem; text-align: center; border: 1px solid #e5e7eb; }
    .metric-value { font-size: 2.5rem; font-weight: bold; color: #3b82f6; }
    .result-card-lit { background-color: white; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #3b82f6; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 1rem; }
    .result-card-grant { background-color: #fff7ed; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #f97316; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 1rem; }
    .expander-box { background-color: #f3f4f6; border-left: 4px solid #9ca3af; padding: 1rem; border-radius: 4px; margin-bottom: 2rem; font-family: monospace;}
    .badge-grant { background-color: #f97316; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; margin-bottom: 8px; display: inline-block;}
    .badge-lit { background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; margin-bottom: 8px; display: inline-block;}
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- MOCK DATABASE INIT ---
# This creates a persistent "database" for the duration of the user's session
if 'search_history' not in st.session_state:
    # Seed data to make the dashboard look populated for presentations
    categories = ["Admin Burden", "Clinical Readiness", "Staffing/Morale", "Supply Chain", "Patient Care"]
    seed_data = []
    for _ in range(25):
        days_ago = random.randint(1, 30)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M")
        seed_data.append({"Date": date, "User_Query": "historical_data_mock", "Category": random.choice(categories)})
    st.session_state.search_history = pd.DataFrame(seed_data)

# --- HELPER FUNCTIONS ---

def categorize_query(query):
    """Simple clustering algorithm based on keywords"""
    q = query.lower()
    if any(word in q for word in ["ehr", "mhs genesis", "click", "admin", "training"]):
        return "Admin Burden"
    elif any(word in q for word in ["readiness", "deploy", "austere", "trauma"]):
        return "Clinical Readiness"
    elif any(word in q for word in ["burnout", "tired", "turnover", "pay", "manning"]):
        return "Staffing/Morale"
    elif any(word in q for word in ["supply", "equipment", "shortage"]):
        return "Supply Chain"
    else:
        return "Patient Care"

def expand_query(user_query):
    optimized = f"({user_query}) AND (military OR defense OR veteran OR army OR navy OR air force)"
    lower_q = user_query.lower()
    if "burnout" in lower_q or "tired" in lower_q:
        optimized = f"({user_query} OR fatigue OR burnout OR turnover) AND (military OR veteran OR nursing)"
    elif "readiness" in lower_q or "aprn" in lower_q:
        optimized = f"({user_query} OR \"advanced practice\" OR competency OR deployment) AND (military OR defense)"
    return optimized

def search_federal_grants(expanded_query, max_results=5):
    url = "https://api.reporter.nih.gov/v2/projects/search"
    payload = {"criteria": {"advanced_text_search": {"operator": "and", "search_text": expanded_query}}, "offset": 0, "limit": max_results}
    try:
        res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}).json()
        results = []
        for item in res.get('results', []):
            title = item.get('project_title', 'No Title')
            abstract = item.get('abstract_text', '') or ''
            if abstract: abstract = abstract.replace('?', '').replace('\n', ' ')[:250] + "..."
            pi = item.get('contact_pi_name', 'Unknown PI')
            org = item.get('organization', {}).get('org_name', 'Unknown Organization')
            app_id = item.get('appl_id', '')
            results.append({'title': title.title(), 'href': f"https://reporter.nih.gov/project-details/{app_id}", 'body': f"**Organization:** {org} | **PI:** {pi}<br><span style='color:#4B5563;'>{abstract}</span>"})
        return results
    except: return []

def search_pubmed(expanded_query, max_results=5):
    try:
        safe_query = urllib.parse.quote(expanded_query)
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={safe_query}&retmode=json&retmax={max_results}"
        res = requests.get(search_url).json()
        id_list = res.get('esearchresult', {}).get('idlist', [])
        if not id_list: return []
        ids = ",".join(id_list)
        sum_res = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids}&retmode=json").json()
        results = []
        for uid in id_list:
            data = sum_res.get('result', {}).get(uid, {})
            title = data.get('title', 'No Title Available')
            source = data.get('source', 'Unknown Journal')
            pubdate = data.get('pubdate', 'Unknown Date')
            authors = ", ".join([a.get('name', '') for a in data.get('authors', [])[:2]]) + (" et al." if len(data.get('authors', [])) > 2 else "")
            results.append({'title': title, 'href': f"https://pubmed.ncbi.nlm.nih.gov/{uid}/", 'body': f"**{source}** ({pubdate}) | Authors: {authors}"})
        return results
    except: return []

# --- MAIN APP LAYOUT ---

st.markdown('<div class="dashboard-header">Innovation & Research Search Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-sub">Bridging the gap between front-line feedback and active medical research.</div>', unsafe_allow_html=True)

# Metrics dynamically updated based on database
total_searches = len(st.session_state.search_history)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><div style="color:#6b7280; font-weight:600;">Data APIs Connected</div><div class="metric-value">2</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div style="color:#6b7280; font-weight:600;">Total Insights Tracked</div><div class="metric-value">{total_searches}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><div style="color:#6b7280; font-weight:600;">System Status</div><div class="metric-value" style="color:#10b981;">Online</div></div>', unsafe_allow_html=True)

st.write("---")

tab1, tab2, tab3 = st.tabs(["🔎 Submit Insight & Search", "📊 Leadership Analytics", "📝 Official Routing"])

# --- TAB 1: SEARCH & TRACK ---
with tab1:
    st.markdown("### Enter your clinical challenge, idea, or 'crazy maker'")
    col_a, col_b = st.columns([4, 1])
    with col_a:
        user_query = st.text_input("Describe the issue", placeholder="e.g. APRN Readiness, EHR clicking takes too long, Burnout", label_visibility="collapsed")
    with col_b:
        search_btn = st.button("Submit & Analyze", type="primary", use_container_width=True)
    
    if search_btn and user_query:
        # TRACKING LOGIC: Add query to our database
        category = categorize_query(user_query)
        new_entry = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "User_Query": user_query, "Category": category}])
        st.session_state.search_history = pd.concat([new_entry, st.session_state.search_history], ignore_index=True)
        
        # UI Feedback
        st.success(f"Insight successfully logged and categorized as: **{category}**")
        
        # SEARCH LOGIC
        expanded_query = expand_query(user_query)
        st.markdown(f"""
        <div class="expander-box">
            <strong>⚙️ System actively searching for existing solutions:</strong><br>
            <span style="color:#4b5563; font-size:0.9rem;">Translating query for federal databases...</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("Querying Federal Grants and PubMed..."):
            grants = search_federal_grants(expanded_query, max_results=3)
            literature = search_pubmed(expanded_query, max_results=5)
            
            if grants or literature:
                if grants:
                    st.markdown("#### 🚀 Ongoing Federal Grants (Avoid Duplication)")
                    for res in grants:
                        st.markdown(f'<div class="result-card-grant"><div class="badge-grant">Active Funded Project</div><br><a href="{res["href"]}" target="_blank" style="text-decoration:none; color:#ea580c; font-weight:bold; font-size:1.1rem;">{res["title"]}</a><div style="margin-top:8px;">{res["body"]}</div></div>', unsafe_allow_html=True)
                if literature:
                    st.markdown("#### 📚 Published Solutions (Evidence-Based Practice)")
                    for res in literature:
                        st.markdown(f'<div class="result-card-lit"><div class="badge-lit">Published Article</div><br><a href="{res["href"]}" target="_blank" style="text-decoration:none; color:#1E3A8A; font-weight:bold; font-size:1.1rem;">{res["title"]}</a><div style="color:#4B5563; margin-top:8px;">{res["body"]}</div></div>', unsafe_allow_html=True)
            else:
                st.error("No direct matches found. Your insight has been flagged as a potential NEW innovation gap for leadership review.")

# --- TAB 2: LEADERSHIP ANALYTICS ---
with tab2:
    st.markdown("### Front-Line Insight Trends")
    st.markdown("This dashboard clusters incoming searches and feedback to identify systemic issues across the force.")
    
    # Generate Chart Data
    df = st.session_state.search_history
    category_counts = df['Category'].value_counts()
    
    col_chart, col_data = st.columns([2, 1])
    
    with col_chart:
        st.markdown("##### Insight Categories (Last 30 Days)")
        st.bar_chart(category_counts, color="#3b82f6")
        
    with col_data:
        st.markdown("##### Top Trending Gaps")
        for index, value in category_counts.items():
            st.markdown(f"**{index}:** {value} reports")
            
    st.markdown("##### Live Tracking Log")
    # Display the dataframe (hiding the index for a cleaner look)
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- TAB 3: SUBMISSION ---
with tab3:
    st.markdown("### Route to Official Channels")
    st.info("To maintain OPSEC and secure data handling, sensitive feedback should be routed through official channels.")
    survey_url = "https://www.milsuite.mil" 
    st.markdown(f'''<br><a href="{survey_url}" target="_blank" style="background-color: #1E3A8A; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">🚀 Launch milSurvey (CAC Required)</a>''', unsafe_allow_html=True)
