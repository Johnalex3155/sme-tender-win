import streamlit as st
import json
import random
from utils.scraper import TenderScraper
from agents.tender_agent import TenderAgent


import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Page Config
st.set_page_config(page_title="SME Tender-Win AI", page_icon="🚀", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { 
        background-color: #1e293b !important; 
        padding: 15px !important; 
        border-radius: 12px !important; 
        border: 1px solid #3b82f6 !important; 
    }
    div[data-testid="stMetricLabel"] > div {
        color: #FFFFFF !important;
        opacity: 1 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #60A5FA !important;
        opacity: 1 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    .proposal-box { background-color: #1e293b; padding: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; color: #ffffff; }
    
    [data-testid="stSidebarUserContent"] {
        gap: 0rem !important;
    }
    .stTighter {
        margin-top: -15px !important;
        margin-bottom: -15px !important;
    }
</style>
    """, unsafe_allow_html=True)

st.title("🚀 SME Tender-Win AI")
st.subheader("Democratizing Government Procurement for Small Businesses")

# --- State Management ---
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_tender' not in st.session_state:
    st.session_state.selected_tender = None
if 'portal_sources' not in st.session_state:
    st.session_state.portal_sources = [
    "https://itida.gov.eg",
    "https://www.caoa.gov.eg",
    "https://www.eehc.gov.eg",
    "https://www.gags.gov.eg",
    "https://www.newcities.gov.eg",
    "https://etenders.gov.eg",
    "https://tra.gov.eg",
    "https://tenderegypt.com\n",
    "https://www.tendersontime.com/egypt-tenders/information-technology-tenders\n",
    "https://eps-gags.gov.eg",
    "https://www.ahram.org.eg/AlAhram/Tenders.aspx\n",
    "https://mcit.gov.eg",
    "https://www.globaltenders.com/egypt/eg-information-technology-tenders\n",
    "https://www.egypttenders.com/tenders.php\n",
    "https://privatesector.moic.gov.eg/en/tenders",
    "https://apa.gov.eg/en/page/announcement/alex-announcement-4/",
    "https://privatesector.moic.gov.eg/ar/tenders",
    "https://idsc.gov.eg"
]

# --- Sidebar: SME Profile & Config ---
st.sidebar.subheader("🏢 SME Profile")
try:
    with open(os.path.join(DATA_DIR, "sme_profile.json"), "r") as f:
        default_profile = json.load(f)
except FileNotFoundError:
    default_profile = {"company_name": "New SME", "niche": "General Tech", "capabilities": [], "past_experience": []}
# Persistent AI Settings
settings_path = os.path.join(DATA_DIR, "ai_settings.json")
try:
    with open(settings_path, "r") as f:
        ai_settings = json.load(f)
except FileNotFoundError:
    ai_settings = {"url": "https://ollama.com/api/chat", "api_key": "", "model": "gemma4:31b"}

st.sidebar.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

st.sidebar.subheader("⚙️ AI Settings")
llm_url = st.sidebar.text_input("Ollama Server URL", value=ai_settings.get("url", "https://ollama.com/api/chat"))
llm_api_key = st.sidebar.text_input("Ollama API Key", value=ai_settings.get("api_key", ""), type="password")

if st.sidebar.button("💾 Save AI Settings"):
    with open(os.path.join(DATA_DIR, "ai_settings.json"), "w") as f:
        json.dump({"url": llm_url, "api_key": llm_api_key, "model": llm_model if 'llm_model' in locals() else "gemma4:31b"}, f)
    st.sidebar.success("Settings Saved!")
    st.rerun()

# Fetch available models
if 'available_models' not in st.session_state:
    st.session_state.available_models = []

if st.sidebar.button("🔄 Refresh Model List"):
    with st.spinner("Fetching models..."):
        st.session_state.available_models = TenderAgent.get_available_models(llm_url, llm_api_key)
    if not st.session_state.available_models:
        st.sidebar.warning("No models found. Check your API Key and URL.")

if st.session_state.available_models:
    llm_model = st.sidebar.selectbox("Model Name", options=st.session_state.available_models)
else:
    llm_model = st.sidebar.text_input("Model Name", value=ai_settings.get("model", "gemma4:31b"))


st.sidebar.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
st.sidebar.subheader("🌐 Manage Sources")
selected_source = st.sidebar.selectbox("Target Portal", st.session_state.portal_sources)
new_source = st.sidebar.text_input("Add New Portal URL")
if st.sidebar.button("➕ Add Source"):
    if new_source and new_source not in st.session_state.portal_sources:
        st.session_state.portal_sources.append(new_source)
        st.rerun()

if st.sidebar.button("🗑️ Delete Selected Source"):
    if selected_source in st.session_state.portal_sources:
        st.session_state.portal_sources.remove(selected_source)
        if not st.session_state.portal_sources:
            st.session_state.portal_sources = ["https://etenders.gov.eg"]
        st.rerun()

# --- Main Area: Search & Crawl ---
st.markdown("### 🎯 Find Opportunities")
mode = st.radio("Discovery Mode", ["Keyword Search (via Google)", "Direct Portal Crawl"], horizontal=True)

with st.form("search_form"):
    col1, col2 = st.columns([4, 1])
    with col1:
        if mode == "Keyword Search (via Google)":
            query = st.text_input("🔍 Keywords", placeholder="e.g., Logistics, Ports, AI Software")
        else:
            query = st.selectbox("🌐 Select Portal to Crawl", st.session_state.portal_sources)
    with col2:
        st.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
        action_button = st.form_submit_button("Get Tenders", use_container_width=True, type="primary")

if action_button:
    if not query:
        st.warning("Please enter a keyword or select a portal.")
    else:
        with st.spinner("Fetching opportunities..."):
            scraper = TenderScraper()
            if mode == "Keyword Search (via Google)":
                results = scraper.search_tenders(query, sources=st.session_state.portal_sources)
            else:
                results = scraper.crawl_portal(query)
            
            st.session_state.search_results = results
            st.session_state.selected_tender = None

# --- Display Results ---
if st.session_state.search_results:
    st.markdown("### 📋 Found Tenders")
    st.write(f"Found {len(st.session_state.search_results)} potential opportunities.")
    
    for idx, res in enumerate(st.session_state.search_results):
        with st.container():
            cols = st.columns([0.8, 0.2])
            with cols[0]:
                st.markdown(f"**{res['title']}**")
                st.caption(res['url'])
            with cols[1]:
                # Analyze button was removed as per user request
                pass

elif not st.session_state.search_results and action_button:
    st.error("📡 No matching tenders found. Try a different query or portal.")

st.markdown("""
    <div style='text-align: center; color: grey; margin-top: 50px; font-size: 0.8rem;'>
    SME Tender-Win AI | Built for the AI Agent Hackathon 2026
    </div>
    """, unsafe_allow_html=True)
