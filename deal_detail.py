"""
NCD Tracker - Deal Detail UI
Detail view with phase-wise checklist tracking
"""

import streamlit as st
import config
from data.excel_manager import ExcelManager
from utils.formatters import *
from utils.helpers import display_success_message

def render_deal_detail():
    """Render deal detail page with checklist"""
    
    # Get selected deal
    company_name = st.session_state.get('selected_deal')
    if not company_name:
        st.error("No deal selected")
        return
    
    excel_mgr = ExcelManager()
    deal = excel_mgr.get_deal_by_company(company_name)
    
    if not deal:
        st.error(f"Deal not found: {company_name}")
        return
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state['page'] = 'dashboard'
        st.rerun()
    
    # Header
    st.markdown(f"# {deal.company_name}")
    
    # Summary row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        badge_color = "#4CAF50" if deal.instrument_type == "Listed NCD" else "#9E9E9E"
        st.markdown(f'<span style="background-color: {badge_color}; color: white; padding: 4px 12px; border-radius: 4px;">{deal.instrument_type}</span>', unsafe_allow_html=True)
        st.caption(f"**{format_amount(deal.issuance_size)}**")
    with col2:
        st.caption("**Funding Date (T)**")
        st.markdown(f"**{format_date(deal.funding_date)}**")
    with col3:
        t_color = config.T_COUNTDOWN_COLORS[deal.get_t_countdown_color()]
        st.caption("**T-Countdown**")
        st.markdown(f'<div style="background-color: {t_color}; color: white; padding: 8px; text-align: center; border-radius: 4px; font-weight: bold; font-size: 1.2em;">{format_t_countdown(deal.funding_date)}</div>', unsafe_allow_html=True)
    with col4:
        st.caption("**Pre-funding overall**")
        pct = deal.get_overall_completion_percentage()
        st.progress(pct / 100)
        st.markdown(f"**{deal.checklist_progress}**")
    
    st.markdown("---")
    
    # Phase tabs
    tab_names = [f"{config.PHASE_ICONS[p]} {p}" for p in config.PHASE_NAMES]
    tabs = st.tabs(tab_names)
    
    for idx, phase in enumerate(config.PHASE_NAMES):
        with tabs[idx]:
            render_phase_checklist(deal, phase, excel_mgr)
    
    # Action buttons
    st.markdown("---")
    col_close, col_delete = st.columns([1, 1])
    
    with col_close:
        if deal.is_fully_funded():
            if st.button("🎯 Mark as Closed & Move to Archive", use_container_width=True, type="primary"):
                st.session_state['show_closure_form'] = True
                st.rerun()
        else:
            pct = deal.get_overall_completion_percentage()
            st.button(f"⏳ Complete all steps ({pct}%) to close deal", disabled=True, use_container_width=True)
    
    with col_delete:
        if st.button("🗑️ Delete Deal", use_container_width=True):
            if st.session_state.get('confirm_delete') == deal.company_name:
                excel_mgr.delete_pipeline_deal(company_name)
                st.success("Deal deleted successfully")
                st.session_state['page'] = 'dashboard'
                st.rerun()
            else:
                st.session_state['confirm_delete'] = deal.company_name
                st.warning("⚠️ Click again to confirm deletion")
    
    # Show closure form if needed
    if st.session_state.get('show_closure_form'):
        render_closure_form(deal, excel_mgr)

def render_phase_checklist(deal, phase, excel_mgr):
    """Render checklist for a specific phase"""
    
    if phase not in deal.checklists:
        st.info(f"No checklist items for {phase}")
        return
    
    checklist = deal.checklists[phase]
    
    # Phase info
    st.markdown(f"### {phase} - {config.PHASE_DESCRIPTIONS.get(phase, '')}")
    st.caption(f"**Timing:** {config.PHASE_TIMINGS.get(phase, 'N/A')}")
    
    # Progress
    completed = checklist.get_completed_count()
    total = checklist.get_total_count()
    pct = checklist.get_completion_percentage()
    
    col_prog, col_stats = st.columns([3, 1])
    with col_prog:
        st.progress(pct / 100)
    with col_stats:
        st.markdown(f"**{completed}/{total} - {pct}%**")
    
    st.markdown("")
    
    # Checklist items
    for item in checklist.items:
        render_checklist_item(deal, phase, item, excel_mgr)

def render_checklist_item(deal, phase, item, excel_mgr):
    """Render individual checklist item"""
    
    col_check, col_content = st.columns([0.5, 9.5])
    
    with col_check:
        # Checkbox
        checked = st.checkbox(
            "",
            value=item.completed,
            key=f"check_{deal.company_name}_{phase}_{item.step_number}",
            label_visibility="collapsed"
        )
        
        # Update if changed
        if checked != item.completed:
            item.completed = checked
            item.status = "Completed" if checked else "Pending"
            deal.update_checklist_progress()
            excel_mgr.update_pipeline_deal(deal.company_name, deal)
            st.rerun()
    
    with col_content:
        # Task title with step number
        task_text = f"**{item.step_number}.** {item.task_title}"
        if item.completed:
            task_text = f"~~{task_text}~~"
        st.markdown(task_text)
        
        # Meta information row
        meta_cols = st.columns([2, 2, 2, 1])
        with meta_cols[0]:
            st.caption(f"👤 **Maker:** {item.maker}")
        with meta_cols[1]:
            if item.timing_note:
                st.caption(f"⏰ {item.timing_note}")
        with meta_cols[2]:
            # Status dropdown
            new_status = st.selectbox(
                "Status",
                options=config.STATUS_OPTIONS,
                index=config.STATUS_OPTIONS.index(item.status),
                key=f"status_{deal.company_name}_{phase}_{item.step_number}",
                label_visibility="collapsed"
            )
            if new_status != item.status:
                item.status = new_status
                excel_mgr.update_pipeline_deal(deal.company_name, deal)
        
        # Sub-notes (expandable)
        if item.sub_notes or st.session_state.get(f"edit_notes_{deal.company_name}_{phase}_{item.step_number}"):
            with st.expander("📝 Notes"):
                notes = st.text_area(
                    "Sub-notes",
                    value=item.sub_notes,
                    key=f"notes_{deal.company_name}_{phase}_{item.step_number}",
                    label_visibility="collapsed",
                    height=60
                )
                if notes != item.sub_notes:
                    item.sub_notes = notes
                    excel_mgr.update_pipeline_deal(deal.company_name, deal)
        
        st.markdown("")

def render_closure_form(deal, excel_mgr):
    """Render deal closure form"""
    from data.data_models import ClosedDeal
    from documents.term_sheet_generator import TermSheetGenerator
    from utils.validators import validate_closure_form
    from utils.helpers import display_error_messages
    
    st.markdown("## 🎯 Close Deal & Move to Archive")
    st.markdown(f"Complete the following details to close **{deal.company_name}** and move it to Closed NCD Deals:")
    
    with st.form("closure_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            isin = st.text_input("ISIN Number *", placeholder="INE123456789", max_chars=12)
            coupon = st.number_input("Coupon Rate (% p.a.) *", min_value=0.0, max_value=25.0, value=9.0, step=0.01, format="%.2f")
        
        with col2:
            tenor = st.number_input("Tenor (Months) *", min_value=1, max_value=120, value=24, step=1)
            maturity_date = st.date_input("Maturity Date *", value=deal.funding_date)
        
        st.markdown("")
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submit = st.form_submit_button("✅ Close Deal & Generate Term Sheet", type="primary", use_container_width=True)
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state['show_closure_form'] = False
            st.rerun()
        
        if submit:
            form_data = {'isin': isin, 'coupon': coupon, 'tenor': tenor, 'maturity_date': maturity_date}
            is_valid, errors = validate_closure_form(form_data)
            
            if not is_valid:
                display_error_messages(errors)
            else:
                try:
                    # Create closed deal
                    closed_deal = ClosedDeal.from_pipeline_deal(deal, isin.upper(), coupon, tenor, maturity_date)
                    
                    # Move to closed
                    excel_mgr.move_to_closed(deal, closed_deal)
                    
                    # Generate term sheet
                    from utils.helpers import create_company_folder
                    company_folder = create_company_folder(deal.company_name, config.ISSUANCE_FOLDER)
                    term_sheet_path = company_folder / f"TermSheet_{isin}.docx"
                    
                    generator = TermSheetGenerator()
                    generator.generate_with_highlights(closed_deal, term_sheet_path)
                    
                    st.success(config.SUCCESS_DEAL_CLOSED)
                    st.success(config.SUCCESS_TERM_SHEET_GENERATED)
                    st.info(f"📄 Term sheet saved to: {term_sheet_path}")
                    
                    st.session_state['show_closure_form'] = False
                    st.session_state['page'] = 'closed_deals'
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error closing deal: {str(e)}")
