"""
NCD Issuance Tracker - Main Application
Streamlit-based tracker for Non-Convertible Debenture issuance pipeline

Author: Trading Champion
Version: 1.0
Date: March 2026
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import config
from excel_manager import ExcelManager
from dashboard import render_dashboard
from new_deal import render_new_deal_form, render_info_panel
from deal_detail import render_deal_detail
from closed_deals import render_closed_deals
from future_scope import render_future_scope

# ===== PAGE CONFIGURATION =====
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS =====
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .deal-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 6px 6px 0 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Info boxes */
    .info-box {
        padding: 1rem;
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== SESSION STATE INITIALIZATION =====
def init_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state['page'] = 'dashboard'
    
    if 'selected_deal' not in st.session_state:
        st.session_state['selected_deal'] = None
    
    if 'show_closure_form' not in st.session_state:
        st.session_state['show_closure_form'] = False
    
    if 'confirm_delete' not in st.session_state:
        st.session_state['confirm_delete'] = None

# ===== SIDEBAR NAVIGATION =====
def render_sidebar():
    """Render sidebar with navigation and info"""
    with st.sidebar:
        # Logo/Title
        st.markdown(f"<h1 class='main-title'>{config.PAGE_ICON} NCD Tracker</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='subtitle'>{config.APP_SUBTITLE}</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        if st.button("🏠 Dashboard", use_container_width=True, type="primary" if st.session_state['page'] == 'dashboard' else "secondary"):
            st.session_state['page'] = 'dashboard'
            st.session_state['selected_deal'] = None
            st.rerun()
        
        if st.button("➕ New Issuance", use_container_width=True, type="primary" if st.session_state['page'] == 'new_deal' else "secondary"):
            st.session_state['page'] = 'new_deal'
            st.rerun()
        
        if st.button("✅ Closed Deals", use_container_width=True, type="primary" if st.session_state['page'] == 'closed_deals' else "secondary"):
            st.session_state['page'] = 'closed_deals'
            st.rerun()
        
        if st.button("🚀 Future Scope", use_container_width=True, type="primary" if st.session_state['page'] == 'future_scope' else "secondary"):
            st.session_state['page'] = 'future_scope'
            st.rerun()
        
        st.markdown("---")
        
        # Quick Stats
        try:
            excel_mgr = ExcelManager()
            pipeline_deals = excel_mgr.load_pipeline_deals()
            closed_deals = excel_mgr.load_closed_deals()
            
            st.markdown("### 📊 Quick Stats")
            st.metric("Pipeline Deals", len(pipeline_deals))
            st.metric("Completed Deals", len(closed_deals))
            
            # Due soon count
            due_soon = sum(1 for deal in pipeline_deals if deal.get_days_until_funding() <= 7)
            if due_soon > 0:
                st.warning(f"⚠️ {due_soon} deal{'s' if due_soon != 1 else ''} due within 7 days")
        
        except Exception as e:
            st.error("Error loading stats")
        
        st.markdown("---")
        
        # File paths info
        with st.expander("⚙️ Configuration"):
            st.caption(f"**Data File:**")
            st.caption(f"`{config.DATA_FILE}`")
            st.caption(f"**Template:**")
            st.caption(f"`{config.TERM_SHEET_TEMPLATE}`")
            
            # Check if files exist
            if Path(config.DATA_FILE).exists():
                st.success("✅ Data file found")
            else:
                st.warning("⚠️ Data file will be created on first use")
            
            if Path(config.TERM_SHEET_TEMPLATE).exists():
                st.success("✅ Template found")
            else:
                st.warning("⚠️ Template not found at configured path")
        
        st.markdown("---")
        
        # Version info
        st.caption("**Version:** 1.0")
        st.caption("**Updated:** March 2026")
        st.caption("**Platform:** Streamlit + Excel")

# ===== MAIN CONTENT ROUTER =====
def render_main_content():
    """Render main content based on current page"""
    page = st.session_state.get('page', 'dashboard')
    
    if page == 'dashboard':
        render_dashboard()
    
    elif page == 'new_deal':
        render_new_deal_form()
        render_info_panel()
    
    elif page == 'deal_detail':
        render_deal_detail()
    
    elif page == 'closed_deals':
        render_closed_deals()
    
    elif page == 'future_scope':
        render_future_scope()
    
    else:
        st.error(f"Unknown page: {page}")
        st.session_state['page'] = 'dashboard'
        st.rerun()

# ===== ERROR HANDLING =====
def handle_error(error):
    """Display user-friendly error messages"""
    st.error("⚠️ An error occurred")
    
    with st.expander("Error Details"):
        st.code(str(error))
    
    st.info("💡 **Troubleshooting Tips:**\n"
            "1. Check that the Excel file path is correct in config.py\n"
            "2. Ensure you have write permissions to the data directory\n"
            "3. Verify all required Python packages are installed\n"
            "4. Try refreshing the page")

# ===== MAIN APPLICATION =====
def main():
    """Main application entry point"""
    try:
        # Initialize session state
        init_session_state()
        
        # Render sidebar
        render_sidebar()
        
        # Render main content
        render_main_content()
        
    except Exception as e:
        handle_error(e)

# ===== RUN APPLICATION =====
if __name__ == "__main__":
    main()
