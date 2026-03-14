"""
NCD Tracker - Dashboard UI
Main dashboard view with summary statistics and deal cards
"""

import streamlit as st
from datetime import date
import config
from data.excel_manager import ExcelManager
from utils.formatters import *
from utils.helpers import calculate_summary_stats, filter_deals_by_type

def render_dashboard():
    """Render main dashboard"""
    
    # Load data
    excel_mgr = ExcelManager()
    all_deals = excel_mgr.load_pipeline_deals()
    
    # Summary statistics bar
    st.markdown("### 📊 Overview")
    stats = calculate_summary_stats(all_deals)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📈 Total Issuances", stats['total'])
    with col2:
        st.metric("✅ Fully Funded", stats['fully_funded'], delta=None, delta_color="normal")
    with col3:
        st.metric("⚡ In Progress", stats['in_progress'])
    with col4:
        st.metric("🔴 Due ≤7 Days", stats['due_soon'], delta=None, delta_color="inverse")
    
    st.markdown("---")
    
    # Filter bar
    col_filter, col_count = st.columns([3, 1])
    with col_filter:
        filter_type = st.radio(
            "Filter:",
            ["All", "Listed NCD", "Unlisted NCD"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with col_count:
        filtered_deals = filter_deals_by_type(all_deals, filter_type)
        st.caption(f"**{len(filtered_deals)} issuance{'s' if len(filtered_deals) != 1 else ''}**")
    
    # Deal cards grid
    if not filtered_deals:
        st.info("ℹ️ No deals in the pipeline. Click '+ New Issuance' to create one.")
        return
    
    # Display deal cards in rows of 3
    for i in range(0, len(filtered_deals), 3):
        cols = st.columns(3)
        for j, deal in enumerate(filtered_deals[i:i+3]):
            with cols[j]:
                render_deal_card(deal)

def render_deal_card(deal):
    """Render individual deal card"""
    
    # Get countdown color
    t_color_category = deal.get_t_countdown_color()
    t_color = config.T_COUNTDOWN_COLORS[t_color_category]
    
    # Card container
    with st.container():
        # Header
        st.markdown(f"### {deal.company_name}")
        
        # Type badge and amount
        col1, col2 = st.columns([2, 1])
        with col1:
            badge_color = "#4CAF50" if deal.instrument_type == "Listed NCD" else "#9E9E9E"
            st.markdown(f'<span style="background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;">{deal.instrument_type}</span>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{format_amount(deal.issuance_size)}**")
        
        # Funding date with T-countdown
        st.markdown(f"📅 **{format_date(deal.funding_date)}**")
        st.markdown(f'<div style="background-color: {t_color}; color: white; padding: 4px; text-align: center; border-radius: 3px; font-weight: bold;">{format_t_countdown(deal.funding_date)}</div>', unsafe_allow_html=True)
        
        st.markdown("")  # Spacing
        
        # Progress section
        st.caption("**Pre-funding progress**")
        overall_pct = deal.get_overall_completion_percentage()
        st.progress(overall_pct / 100)
        st.caption(deal.checklist_progress)
        
        # Phase progress mini-icons
        phase_cols = st.columns(5)
        for idx, phase in enumerate(config.PHASE_NAMES):
            with phase_cols[idx]:
                if phase in deal.checklists:
                    checklist = deal.checklists[phase]
                    completed = checklist.get_completed_count()
                    total = checklist.get_total_count()
                    icon = config.PHASE_ICONS.get(phase, "📋")
                    st.caption(f"{icon}")
                    st.caption(f"{completed}/{total}")
        
        # View button
        if st.button("📝 View Details", key=f"view_{deal.company_name}", use_container_width=True):
            st.session_state['selected_deal'] = deal.company_name
            st.session_state['page'] = 'deal_detail'
            st.rerun()
        
        st.markdown("---")
