"""
NCD Tracker - Dashboard UI + Future Scope
Merged: dashboard.py + future_scope.py
Compact card layout matching reference design.
Includes term sheet draft generation from pipeline cards.
"""

import streamlit as st
from datetime import date
from pathlib import Path
import io

import config
from data_store import DataStore
from utils import (
    calculate_summary_stats, filter_deals_by_type,
    format_amount, format_date, format_t_countdown, create_company_folder
)
from constants import PHASE_DESCRIPTIONS, PHASE_TIMINGS


# ══════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════

def render_dashboard():
    """Main dashboard — summary stats + compact deal cards."""

    # ── data ──────────────────────────────────────
    ds        = DataStore()
    all_deals = ds.load_pipeline_deals()
    stats     = calculate_summary_stats(all_deals)

    # ── top header row ─────────────────────────────
    h_col1, h_col2 = st.columns([4, 1])
    with h_col1:
        st.markdown(
            "<h2 style='margin:0; color:#1e3a8a;'>📊 NCD Issuance Tracker</h2>"
            "<p style='margin:0; color:#64748b; font-size:0.95rem;'>"
            "Structured Product Solutions — Issuer Readiness</p>",
            unsafe_allow_html=True,
        )
    with h_col2:
        if st.button("➕ New Issuance", type="primary", use_container_width=True):
            st.session_state['page'] = 'new_deal'
            st.rerun()

    st.markdown("")

    # ── summary stats ──────────────────────────────
    _render_summary_stats(stats)

    st.markdown("---")

    # ── filter bar ─────────────────────────────────
    fc, cc = st.columns([3, 1])
    with fc:
        filter_type = st.radio(
            "Filter:", ["All", "Listed NCD", "Unlisted NCD"],
            horizontal=True, label_visibility="collapsed",
        )
    filtered = filter_deals_by_type(all_deals, filter_type)
    with cc:
        st.caption(f"**{len(filtered)} issuance{'s' if len(filtered) != 1 else ''}**")

    # ── deal cards ─────────────────────────────────
    if not filtered:
        st.info("ℹ️ No deals in pipeline. Click '➕ New Issuance' to create one.")
        return

    for i in range(0, len(filtered), 3):
        cols = st.columns(3, gap="medium")
        for j, deal in enumerate(filtered[i:i + 3]):
            with cols[j]:
                _render_deal_card(deal)


def _render_summary_stats(stats):
    """4-metric summary bar."""
    col1, col2, col3, col4 = st.columns(4)

    _metric_box(col1, str(stats['total']),        "Total Issuances",  "#1e3a8a", "🏦")
    _metric_box(col2, str(stats['fully_funded']), "Fully Funded",     "#15803d", "✅")
    _metric_box(col3, str(stats['in_progress']),  "In Progress",      "#b45309", "⚡")
    _metric_box(col4, str(stats['due_soon']),     "Due ≤7 Days",      "#dc2626", "🔴")


def _metric_box(col, value, label, color, icon):
    with col:
        st.markdown(
            f"""<div style="
                background:{color}12; border:1px solid {color}40;
                border-radius:8px; padding:14px 18px; text-align:center;">
                <div style="font-size:2rem; font-weight:700; color:{color};">{icon} {value}</div>
                <div style="font-size:0.85rem; color:#475569; margin-top:4px;">{label}</div>
            </div>""",
            unsafe_allow_html=True,
        )


def _render_deal_card(deal):
    """Compact deal card matching reference image."""
    days     = deal.get_days_until_funding()
    t_color  = config.T_COUNTDOWN_COLORS[deal.get_t_countdown_color()]
    badge_bg = "#166534" if "listed" in deal.instrument_type.lower() and "unlisted" not in deal.instrument_type.lower() else "#374151"
    t_label  = format_t_countdown(deal.funding_date)
    t_date   = format_date(deal.funding_date)

    # Card wrapper
    st.markdown(
        f"""<div style="
            border:1px solid #e2e8f0; border-radius:10px;
            padding:14px 16px; background:#fff;
            box-shadow:0 1px 4px rgba(0,0,0,0.07); margin-bottom:4px;">

            <!-- row 1: company name + T-date -->
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="font-size:1rem; font-weight:700; color:#1e293b; flex:1;">{deal.company_name}</div>
                <div style="font-size:0.75rem; color:#64748b; white-space:nowrap; margin-left:8px;">
                    T = {t_date}
                </div>
            </div>

            <!-- row 2: badge + amount + countdown -->
            <div style="display:flex; align-items:center; gap:8px; margin-top:8px; flex-wrap:wrap;">
                <span style="background:{badge_bg}; color:#fff; font-size:0.72rem;
                    padding:2px 8px; border-radius:4px;">{deal.instrument_type}</span>
                <span style="color:#475569; font-size:0.85rem; font-weight:600;">
                    ₹{deal.issuance_size:,.0f} Cr</span>
                <span style="background:{t_color}; color:#fff; font-size:0.78rem;
                    font-weight:700; padding:2px 10px; border-radius:12px; margin-left:auto;">
                    {t_label}</span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Progress bar (Streamlit native)
    pct = deal.get_overall_completion_percentage()
    st.caption(f"Pre-funding progress &nbsp;&nbsp; **{deal.checklist_progress}**")
    st.progress(pct / 100)

    # Phase mini-icons
    phase_cols = st.columns(len(config.PHASE_NAMES))
    for idx, phase in enumerate(config.PHASE_NAMES):
        with phase_cols[idx]:
            if phase in deal.checklists:
                cl = deal.checklists[phase]
                st.markdown(
                    f"<div style='text-align:center; font-size:0.75rem; color:#64748b;'>"
                    f"{config.PHASE_ICONS.get(phase,'📋')}<br>"
                    f"<b>{cl.get_completed_count()}/{cl.get_total_count()}</b></div>",
                    unsafe_allow_html=True,
                )

    # Action buttons
    b1, b2 = st.columns(2)
    with b1:
        if st.button("📝 Details", key=f"detail_{deal.company_name}", use_container_width=True):
            st.session_state['selected_deal'] = deal.company_name
            st.session_state['page']          = 'deal_detail'
            st.rerun()
    with b2:
        if st.button("📄 Term Sheet", key=f"ts_{deal.company_name}", use_container_width=True):
            _generate_draft_term_sheet(deal)

    st.markdown("<hr style='margin:8px 0; border-color:#f1f5f9;'>", unsafe_allow_html=True)


def _generate_draft_term_sheet(deal):
    """Generate a draft term sheet for a pipeline deal and offer download."""
    try:
        from term_sheet import TermSheetGenerator
        import tempfile, os

        gen = TermSheetGenerator()

        # Use a temp file for the docx
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = tmp.name

        gen.generate_draft_for_pipeline(deal, tmp_path)

        with open(tmp_path, "rb") as f:
            docx_bytes = f.read()
        os.unlink(tmp_path)

        safe_name = "".join(c if c.isalnum() or c in ('_', '-') else '_'
                            for c in deal.company_name)
        filename  = f"DraftTermSheet_{safe_name}.docx"

        st.download_button(
            label     = f"⬇️ Download Draft — {deal.company_name}",
            data      = docx_bytes,
            file_name = filename,
            mime      = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key       = f"dl_ts_{deal.company_name}",
        )
        st.success("✅ Draft term sheet ready — click above to download.")

    except FileNotFoundError:
        st.warning("⚠️ Term sheet template not found. "
                   f"Please place it at:\n`{config.TERM_SHEET_TEMPLATE}`")
    except Exception as e:
        st.error(f"Error generating term sheet: {e}")


# ══════════════════════════════════════════════════
#  FUTURE SCOPE
# ══════════════════════════════════════════════════

def render_future_scope():
    st.markdown("## 🚀 Future Enhancements — Phase 2")
    st.markdown("Planned features and improvements for upcoming releases")

    sections = [
        ("🔐 Authentication & Access Control", [
            "**User authentication**: Role-based login (Admin, Manager, Viewer)",
            "**Permission levels**: Maker / Checker / Admin roles",
            "**Audit trail**: Track who made changes and when",
            "**Multi-user editing**: Team collaboration support",
        ]),
        ("🔗 Google Sheets Integration (Phase 2)", [
            "**Real-time persistence**: Replace Excel with Google Sheets API",
            "**Cloud sync**: All deal data auto-saved to Google Sheets",
            "**Access control**: Restrict sheet access to authorised users",
            "**Offline fallback**: Excel backup when Google Sheets unavailable",
        ]),
        ("⚡ Advanced Features", [
            "**Email notifications**: Reminders for T-days and overdue tasks",
            "**Bulk import/export**: Multiple deals at once",
            "**ISIN auto-tracking**: NSDL/CDSL integration",
            "**AI term sheet comparison**: Automated document review",
        ]),
        ("📊 Analytics & Reporting", [
            "**Dashboard analytics**: Trends, completion rates, time-to-funding",
            "**Custom reports**: By date range, asset class, instrument type",
            "**PDF/PowerPoint export**: Presentation-ready reports",
        ]),
    ]

    for title, items in sections:
        st.markdown(f"### {title}")
        for item in items:
            st.markdown(f"- {item}")
        st.markdown("---")

    st.markdown("### 💬 Share Your Ideas")
    with st.form("feedback_form"):
        feature_request = st.text_area("Feature Request / Feedback",
                                       placeholder="Describe the feature you'd like to see…",
                                       height=120)
        priority = st.radio("Priority", ["Nice to have", "Important", "Critical"], horizontal=True)
        if st.form_submit_button("📨 Submit Feedback", use_container_width=True):
            if feature_request:
                st.success("✅ Thank you for your feedback!")
                st.balloons()
