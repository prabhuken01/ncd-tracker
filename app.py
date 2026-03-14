"""
Issuance Tracker - Main Application
Streamlit-based tracker for Non-Convertible Debenture issuance pipeline

Author: Trading Champion
Version: 2.0
Date: March 2026
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import config
from data_store import DataStore
from dashboard import render_dashboard, render_future_scope
from deal_pages import render_new_deal_form, render_info_panel, render_deal_detail, render_closed_deals

# ===== PAGE CONFIGURATION =====
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== FORCE LIGHT THEME CSS =====
st.markdown("""
<style>
    /* ── Force light background everywhere ── */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stMain"] {
        background-color: #f8fafc !important;
        color: #1e293b !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }

    /* ── Override dark-mode defaults ── */
    html, body {
        color-scheme: light !important;
    }

    /* ── Headings & text ── */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
    }

    /* ── Main title ── */
    .main-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 0.5rem;
    }

    /* ── Cards ── */
    .deal-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
    }

    /* ── Metric values ── */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1e293b !important;
    }

    /* ── Progress bar colour ── */
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 18px;
        border-radius: 6px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu  { visibility: hidden; }
    footer     { visibility: hidden; }

    /* ── Info / alert boxes ── */
    .info-box {
        padding: 1rem;
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 4px;
        margin: 1rem 0;
    }

    /* ── Containers (native border=True) ── */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
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

    if 'storage_mode' not in st.session_state:
        st.session_state['storage_mode'] = '📁 Local Folder'


# ===== SIDEBAR NAVIGATION =====
def render_sidebar():
    """Render sidebar with navigation, storage toggle, and info"""
    with st.sidebar:
        # ── Logo / Title ──
        st.markdown(
            "<h1 class='main-title'>📊 Issuance Tracker</h1>"
            "<p class='subtitle'>Structured Product Solutions</p>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── Navigation ──
        st.markdown("### 🧭 Navigation")

        nav_items = [
            ("🏠 Dashboard",      "dashboard"),
            ("➕ New Issuance",   "new_deal"),
            ("✅ Closed Deals",   "closed_deals"),
            ("🚀 Future Scope",   "future_scope"),
        ]
        for label, key in nav_items:
            btn_type = "primary" if st.session_state['page'] == key else "secondary"
            if st.button(label, use_container_width=True, type=btn_type, key=f"nav_{key}"):
                st.session_state['page'] = key
                if key != 'deal_detail':
                    st.session_state['selected_deal'] = None
                st.rerun()

        st.markdown("---")

        # ── Storage Mode Toggle ──
        st.markdown("### 🗄️ Storage Mode")
        storage_choice = st.radio(
            "Select storage",
            ["📁 Local Folder", "☁️ Google Drive (WIP)"],
            index=0 if st.session_state['storage_mode'] == '📁 Local Folder' else 1,
            label_visibility="collapsed",
        )
        st.session_state['storage_mode'] = storage_choice

        if storage_choice == "☁️ Google Drive (WIP)":
            st.info("⚠️ Google Drive mode is coming soon.", icon="ℹ️")
            with st.expander("📋 Setup Instructions"):
                st.markdown("""
**To enable Google Sheets / Drive sync:**

1. **Create a Google Cloud project**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Create a new project (e.g. `ncd-tracker`)

2. **Enable APIs**
   - Enable **Google Sheets API**
   - Enable **Google Drive API**

3. **Create Service Account**
   - IAM & Admin → Service Accounts → Create
   - Role: **Editor**
   - Download JSON key file → save as `service_account.json`
   - Place in `Code_Streamlit/` folder

4. **Share your Sheet**
   - Open your Google Sheet
   - Share → paste the service account email (ends with `@...iam.gserviceaccount.com`)
   - Give **Editor** access

5. **Add to Streamlit secrets**
   - On Streamlit Cloud: Settings → Secrets
   - Add: `GOOGLE_SHEETS_KEY = <JSON content>`

*Contact your admin to complete this setup.*
""")

        st.markdown("---")

        # ── Quick Stats ──
        try:
            ds = DataStore()
            pipeline_deals = ds.load_pipeline_deals()
            closed_deals_list = ds.load_closed_deals()

            st.markdown("### 📊 Quick Stats")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Pipeline", len(pipeline_deals))
            with col_b:
                st.metric("Closed", len(closed_deals_list))

            due_soon = sum(1 for deal in pipeline_deals if deal.get_days_until_funding() <= 7)
            if due_soon > 0:
                st.warning(f"⚠️ {due_soon} deal{'s' if due_soon != 1 else ''} due ≤ 7 days")

        except Exception:
            st.error("Error loading stats")

        st.markdown("---")

        # ── Config info ──
        with st.expander("⚙️ Configuration"):
            st.caption("**Data File:**")
            st.caption(f"`{config.DATA_FILE.name}`")
            st.caption("**Template:**")
            st.caption(f"`{config.TERM_SHEET_TEMPLATE.name}`")
            st.caption("**Issuance Folder:**")
            st.caption(f"`{config.ISSUANCE_FOLDER}`")

            if Path(config.DATA_FILE).exists():
                st.success("✅ Data file found")
            else:
                st.info("ℹ️ Data file will be created on first save")

            if Path(config.TERM_SHEET_TEMPLATE).exists():
                st.success("✅ Template found")
            else:
                st.warning("⚠️ Term_Sheet_Template.docx not found")

        st.markdown("---")
        st.caption("**Version:** 2.0  |  March 2026")


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
    st.error("⚠️ An unexpected error occurred")
    with st.expander("Error Details"):
        st.code(str(error))
    st.info(
        "💡 **Troubleshooting Tips:**\n"
        "1. Check the Excel file path in config.py\n"
        "2. Ensure write permissions on the data directory\n"
        "3. Verify all required packages are installed\n"
        "4. Try refreshing the page"
    )


# ===== MAIN APPLICATION =====
def main():
    """Main application entry point"""
    try:
        init_session_state()
        render_sidebar()
        render_main_content()
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    main()
