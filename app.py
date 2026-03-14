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
from data_store import DataStore, GSheetDataStore, get_data_store
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
    /* ══════════════════════════════════════════
       1. GLOBAL LIGHT BACKGROUND
       Covers all Streamlit layout containers across
       different Streamlit versions.
    ══════════════════════════════════════════ */
    html, body {
        background-color: #f8fafc !important;
        color-scheme: light !important;
    }
    .stApp,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stMain"],
    [data-testid="block-container"],
    [data-testid="stBottom"],
    [data-testid="stHeader"],
    [data-testid="stDecoration"],
    [data-testid="stToolbar"],
    section.main,
    section.main > div,
    .main .block-container {
        background-color: #f8fafc !important;
        color: #1e293b !important;
    }

    /* ══════════════════════════════════════════
       2. SIDEBAR — white with light border
    ══════════════════════════════════════════ */
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    /* All NON-BUTTON text in sidebar dark — excludes primary button children */
    [data-testid="stSidebar"] *:not([data-testid="baseButton-primary"]):not([data-testid="baseButton-primary"] *) {
        color: #1e293b !important;
    }
    /* Sidebar headings */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1e3a8a !important;
    }

    /* ══════════════════════════════════════════
       3. BUTTONS — primary blue (white text),
          secondary light (dark text)
       Rule must come AFTER the sidebar * rule so
       primary button text is always white even in
       the sidebar.
    ══════════════════════════════════════════ */
    /* Secondary / default buttons */
    [data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background-color: #f1f5f9 !important;
        color: #374151 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
    }
    [data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        background-color: #e2e8f0 !important;
        color: #111827 !important;
        border-color: #9ca3af !important;
    }

    /* Primary buttons — dark blue bg, ALWAYS white text */
    [data-testid="baseButton-primary"],
    button[kind="primary"] {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
    }
    [data-testid="baseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background-color: #1e40af !important;
    }
    /* Force white on every child element inside primary buttons.
       This overrides the sidebar * rule which directly targets child nodes. */
    [data-testid="baseButton-primary"] p,
    [data-testid="baseButton-primary"] span,
    [data-testid="baseButton-primary"] div,
    [data-testid="baseButton-primary"] label,
    button[kind="primary"] p,
    button[kind="primary"] span,
    button[kind="primary"] div {
        color: #ffffff !important;
        background-color: transparent !important;
    }

    /* ══════════════════════════════════════════
       4. PROGRESS BAR — light gray track, blue fill
    ══════════════════════════════════════════ */
    /* Track (outer wrapper) */
    .stProgress > div {
        background-color: #e2e8f0 !important;
        border-radius: 100px !important;
    }
    /* Fill */
    .stProgress > div > div {
        background-color: #3b82f6 !important;
        border-radius: 100px !important;
    }
    /* Alternate selectors for Streamlit versions */
    [role="progressbar"] {
        background-color: #e2e8f0 !important;
        border-radius: 100px !important;
    }
    [role="progressbar"] > div {
        background-color: #3b82f6 !important;
        border-radius: 100px !important;
    }

    /* ══════════════════════════════════════════
       5. METRICS — dark text on white bg
    ══════════════════════════════════════════ */
    [data-testid="stMetric"] {
        background-color: transparent !important;
    }
    [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-size: 1.8rem;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #475569 !important;
    }

    /* ══════════════════════════════════════════
       6. TEXT ELEMENTS — always dark on light bg
       NOTE: 'span' is intentionally excluded here so that
       inline color styles (e.g. color:#fff on coloured badges)
       are NOT overridden by this rule.
    ══════════════════════════════════════════ */
    h1, h2, h3, h4, h5, h6 { color: #1e293b !important; }
    p, li, label            { color: #1e293b !important; }
    .stMarkdown, .stText    { color: #1e293b !important; }
    [data-testid="stCaption"]          { color: #64748b !important; }
    [data-testid="stCaptionContainer"] { color: #64748b !important; }
    /* Streamlit-specific text spans only — scoped so inline colours survive */
    [data-testid="stMarkdownContainer"] > p > span:not([style*="color"]) { color: #1e293b; }

    /* ══════════════════════════════════════════
       7. TABS — clean white active, light gray bar
    ══════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f1f5f9 !important;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #475569 !important;
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0 !important;
        color: #1e293b !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        font-weight: 700;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* ══════════════════════════════════════════
       8. INPUT WIDGETS — white bg, dark text
    ══════════════════════════════════════════ */
    .stSelectbox [data-baseweb="select"] > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border-color: #d1d5db !important;
    }

    /* ══════════════════════════════════════════
       9. CONTAINERS / CARDS
    ══════════════════════════════════════════ */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }

    /* ══════════════════════════════════════════
       10. EXPANDER / ALERT BOXES
    ══════════════════════════════════════════ */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary {
        color: #1e293b !important;
    }
    /* Info / success / warning alerts — keep colorful but light */
    [data-testid="stAlert"] {
        border-radius: 8px;
    }

    /* ══════════════════════════════════════════
       11. RADIO BUTTONS — readable labels
    ══════════════════════════════════════════ */
    [data-testid="stRadio"] label {
        color: #374151 !important;
        font-size: 0.9rem;
    }
    [data-testid="stRadio"] > div {
        gap: 4px;
    }

    /* ══════════════════════════════════════════
       12. DATAFRAME / TABLE
    ══════════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border-radius: 8px;
    }

    /* ══════════════════════════════════════════
       13. HIDE STREAMLIT BRANDING
    ══════════════════════════════════════════ */
    #MainMenu  { visibility: hidden; }
    footer     { visibility: hidden; }

    /* ══════════════════════════════════════════
       14. CUSTOM CLASSES
    ══════════════════════════════════════════ */
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
    .info-box {
        padding: 1rem;
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 4px;
        margin: 1rem 0;
        color: #1e3a8a !important;
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
        # Auto-select Google Sheets if credentials are available (file OR Streamlit Secrets)
        if config.google_creds_available():
            st.session_state['storage_mode'] = '☁️ Google Drive'
        else:
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
        options     = ["📁 Local Folder", "☁️ Google Drive"]
        current_idx = 1 if st.session_state['storage_mode'] == '☁️ Google Drive' else 0
        storage_choice = st.radio(
            "Select storage",
            options,
            index=current_idx,
            label_visibility="collapsed",
        )
        st.session_state['storage_mode'] = storage_choice

        creds_ok = config.google_creds_available()
        if storage_choice == "☁️ Google Drive":
            if creds_ok:
                if config.GOOGLE_CREDS_FILE.exists():
                    st.success("✅ service_account.json found", icon="🔑")
                else:
                    st.success("✅ Credentials via Streamlit Secrets", icon="🔑")
                # Try to show spreadsheet link
                try:
                    _gs = GSheetDataStore()
                    st.markdown(f"[📊 Open Google Sheet]({_gs.spreadsheet_url})")
                    st.caption("Google Sheets is active ✅")
                except RuntimeError:
                    # Sheet not yet created/shared — show concise next-step tip
                    with st.expander("📋 One-time sheet setup needed", expanded=True):
                        try:
                            import gspread
                            _gc = GSheetDataStore.__new__(GSheetDataStore)
                            _gc.file_path = config.DATA_FILE
                            _gc.gc = GSheetDataStore._get_gspread_client(_gc)
                            sa_email = _gc.gc.auth.service_account_email
                        except Exception:
                            sa_email = "your-service-account@project.iam.gserviceaccount.com"
                        st.markdown(f"""
**Create the Google Sheet (1 minute):**

1. Open [drive.google.com](https://drive.google.com)
2. **New → Google Sheets** → rename to: `Issuance Tracker`
3. **Share** with Editor access:
   `{sa_email}`
4. Refresh this app ✅
""")
                except Exception as _e:
                    st.warning(f"Connection issue: {_e}")
            else:
                st.warning("⚠️ No credentials found.")
                with st.expander("📋 Setup Instructions"):
                    st.markdown("""
**To enable Google Sheets:**

1. **Google Cloud** → IAM → Service Accounts → create one
2. **Keys tab** → Add Key → JSON → rename to `service_account.json`
3. **Enable APIs:** Google Sheets API + Google Drive API
4. **Streamlit Cloud** → Settings → Secrets:
   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "..."
   private_key = "..."
   client_email = "..."
   ...
   ```
5. Create a Google Sheet named **`Issuance Tracker`** and share it with the service account email
""")

        st.markdown("---")

        # ── Quick Stats ──
        try:
            ds = get_data_store()
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
