"""
NCD Tracker - Deal Pages
Merged: new_deal.py + deal_detail.py + closed_deals.py
All deal-lifecycle UI: creation, checklist tracking, closure, archive view.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

import config
from data_store import DataStore
from models import PipelineDeal, ClosedDeal, validate_new_deal_form, validate_closure_form
from utils import (
    format_amount, format_date, format_t_countdown, format_percentage,
    display_error_messages, display_success_message, create_company_folder,
)
from constants import PHASE_DESCRIPTIONS, PHASE_TIMINGS


# ══════════════════════════════════════════════════
#  NEW DEAL FORM
# ══════════════════════════════════════════════════

def render_new_deal_form():
    st.markdown("## 📝 New Issuance — Deal Initiation")
    st.markdown("Complete the form below to create a new NCD issuance in the pipeline.")

    with st.form("new_deal_form"):
        company_name = st.text_input(
            "Issuer Name *",
            help=config.TOOLTIPS['company_name'],
            placeholder="Enter full legal name of issuer",
        )

        col1, col2 = st.columns(2)
        with col1:
            instrument_type = st.selectbox(
                "Instrument Type *",
                options=config.INSTRUMENT_TYPES,
                help=config.TOOLTIPS['instrument_type'],
            )
        with col2:
            issuer_type = st.selectbox(
                "Issuer Type (FS / EF) *",
                options=config.ISSUER_TYPES,
                help="FS = Financial Sector (NBFC/HFC); EF = Enterprise Finance (Corporate)",
            )

        col3, col4 = st.columns(2)
        with col3:
            asset_class = st.selectbox(
                "Asset Class *",
                options=config.ASSET_CLASSES,
                help=config.TOOLTIPS['asset_class'],
            )
        with col4:
            issuance_size = st.number_input(
                f"Quantum (₹ Cr) *",
                min_value=float(config.MIN_ISSUANCE_SIZE),
                max_value=float(config.MAX_ISSUANCE_SIZE),
                value=100.0, step=10.0, format="%.2f",
                help=config.TOOLTIPS['issuance_size'],
            )

        col5, col6 = st.columns(2)
        with col5:
            default_date = date.today() + timedelta(days=30)
            funding_date = st.date_input(
                "Tentative Issuance Date (T-Day) *",
                value=default_date,
                min_value=date.today() - timedelta(days=90),
                max_value=date.today() + timedelta(days=365),
                help=config.TOOLTIPS['funding_date'],
                format=config.DATE_INPUT_FORMAT,
            )
        with col6:
            rating = st.selectbox(
                "Credit Rating",
                options=["N/A"] + config.RATING_OPTIONS,
                help=config.TOOLTIPS['rating'],
            )

        security = st.selectbox(
            "Security Type",
            options=config.SECURITY_TYPES,
            help=config.TOOLTIPS['security'],
        )

        st.caption("* Required fields")

        c_submit, c_cancel = st.columns(2)
        with c_submit:
            submit = st.form_submit_button("✅ Create Deal", use_container_width=True, type="primary")
        with c_cancel:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

        if cancel:
            st.session_state['page'] = 'dashboard'
            st.rerun()

        if submit:
            form_data = {
                'company_name':   company_name,
                'instrument_type': instrument_type,
                'issuer_type':    issuer_type,
                'issuance_size':  issuance_size,
                'funding_date':   funding_date,
            }
            ok, errors = validate_new_deal_form(form_data)
            if not ok:
                st.error("⚠️ Please fix the following errors:")
                display_error_messages(errors)
            else:
                ds = DataStore()
                if ds.company_exists(company_name):
                    st.error(config.ERROR_DUPLICATE_ENTRY)
                else:
                    try:
                        checklists = ds.initialize_checklist_for_deal(instrument_type)
                        new_deal   = PipelineDeal(
                            company_name    = company_name,
                            instrument_type = instrument_type,
                            issuer_type     = issuer_type,
                            asset_class     = asset_class,
                            issuance_size   = issuance_size,
                            funding_date    = funding_date,
                            rating          = rating,
                            security        = security,
                            checklists      = checklists,
                            created_date    = date.today(),
                            status          = "In Progress",
                        )
                        new_deal.update_checklist_progress()
                        ds.save_pipeline_deal(new_deal)

                        # Create company folder
                        try:
                            create_company_folder(company_name, config.ISSUANCE_FOLDER)
                        except Exception:
                            pass

                        st.success(config.SUCCESS_DEAL_CREATED)
                        st.balloons()
                        st.session_state['selected_deal'] = company_name
                        st.session_state['page']          = 'deal_detail'
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error creating deal: {e}")


def render_info_panel():
    with st.sidebar:
        st.markdown("### ℹ️ Deal Initiation Guide")
        st.markdown("""
**Required:**
- Issuer legal name
- NCD type (Listed / Unlisted)
- Issuer Type (FS / EF)
- Quantum in ₹ Cr
- Tentative issuance date

**After creating:** you'll be taken to the 5-phase checklist tracker.
        """)
        st.markdown("---")
        st.caption("💡 Deals start as 'In Progress' and become 'Fully Funded' when all checklist items are done.")


# ══════════════════════════════════════════════════
#  DEAL DETAIL / CHECKLIST
# ══════════════════════════════════════════════════

def render_deal_detail():
    company_name = st.session_state.get('selected_deal')
    if not company_name:
        st.error("No deal selected")
        return

    ds   = DataStore()
    deal = ds.get_deal_by_company(company_name)
    if not deal:
        st.error(f"Deal not found: {company_name}")
        return

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state['page'] = 'dashboard'
        st.rerun()

    # ── header ────────────────────────────────────
    st.markdown(f"# {deal.company_name}")

    t_color = config.T_COUNTDOWN_COLORS[deal.get_t_countdown_color()]
    badge_bg = "#166534" if "unlisted" not in deal.instrument_type.lower() else "#374151"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<span style="background:{badge_bg}; color:#fff; padding:4px 12px; border-radius:4px;">'
            f'{deal.instrument_type}</span><br>'
            f'<b>₹{deal.issuance_size:,.0f} Cr</b>',
            unsafe_allow_html=True,
        )
    with c2:
        st.caption("**Issuer Type**")
        st.markdown(f"**{deal.issuer_type}** — {deal.asset_class}")
    with c3:
        st.caption("**Funding Date (T)**")
        st.markdown(f"**{format_date(deal.funding_date)}**")
        st.markdown(
            f'<div style="background:{t_color}; color:#fff; padding:4px 12px; '
            f'border-radius:12px; display:inline-block; font-weight:700;">'
            f'{format_t_countdown(deal.funding_date)}</div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.caption("**Pre-funding overall**")
        pct = deal.get_overall_completion_percentage()
        st.progress(pct / 100)
        st.markdown(f"**{deal.checklist_progress}**")

    st.markdown("---")

    # ── phase tabs ────────────────────────────────
    tab_names = [f"{config.PHASE_ICONS[p]} {p} {_phase_badge(deal, p)}"
                 for p in config.PHASE_NAMES]
    tabs = st.tabs(tab_names)

    for idx, phase in enumerate(config.PHASE_NAMES):
        with tabs[idx]:
            _render_phase_checklist(deal, phase, ds)

    # ── actions ───────────────────────────────────
    st.markdown("---")
    ca, cb, cc = st.columns(3)

    with ca:
        if deal.is_fully_funded():
            if st.button("🎯 Close & Archive Deal", use_container_width=True, type="primary"):
                st.session_state['show_closure_form'] = True
                st.rerun()
        else:
            pct = deal.get_overall_completion_percentage()
            st.button(f"⏳ {pct}% — complete all steps to close", disabled=True, use_container_width=True)

    with cb:
        if st.button("📄 Draft Term Sheet", use_container_width=True):
            _generate_pipeline_term_sheet(deal)

    with cc:
        if st.button("🗑️ Delete Deal", use_container_width=True):
            if st.session_state.get('confirm_delete') == deal.company_name:
                ds.delete_pipeline_deal(company_name)
                st.success("Deal deleted successfully")
                st.session_state['page'] = 'dashboard'
                st.rerun()
            else:
                st.session_state['confirm_delete'] = deal.company_name
                st.warning("⚠️ Click again to confirm deletion")

    if st.session_state.get('show_closure_form'):
        _render_closure_form(deal, ds)


def _phase_badge(deal, phase):
    if phase not in deal.checklists:
        return ""
    cl  = deal.checklists[phase]
    pct = cl.get_completion_percentage()
    if pct == 100:
        return "✅"
    elif pct > 0:
        return f"({pct}%)"
    return ""


def _render_phase_checklist(deal, phase, ds):
    if phase not in deal.checklists:
        st.info(f"No checklist items for {phase}")
        return

    cl = deal.checklists[phase]

    desc   = PHASE_DESCRIPTIONS.get(phase, phase)
    timing = PHASE_TIMINGS.get(phase, "")
    st.markdown(f"### {desc}")
    if timing:
        st.caption(f"⏰ **Timing:** {timing}")

    completed = cl.get_completed_count()
    total     = cl.get_total_count()
    pct       = cl.get_completion_percentage()

    pr_col, st_col = st.columns([4, 1])
    with pr_col:
        st.progress(pct / 100)
    with st_col:
        st.markdown(f"**{completed}/{total} — {pct}%**")

    st.markdown("")

    for item in cl.items:
        _render_checklist_item(deal, phase, item, ds)


def _render_checklist_item(deal, phase, item, ds):
    col_check, col_content = st.columns([0.5, 9.5])

    with col_check:
        checked = st.checkbox(
            "",
            value     = item.completed,
            key       = f"chk_{deal.company_name}_{phase}_{item.step_number}",
            label_visibility="collapsed",
        )
        if checked != item.completed:
            item.completed = checked
            item.status    = "Completed" if checked else "Pending"
            deal.update_checklist_progress()
            ds.update_pipeline_deal(deal.company_name, deal)
            st.rerun()

    with col_content:
        title = f"**{item.step_number:02d}.** {item.task_title}"
        if item.listed_only:
            title += " *(Listed only)*"
        if item.completed:
            title = f"~~{title}~~"
        st.markdown(title)

        m1, m2, m3 = st.columns([2, 2, 2])
        with m1:
            st.caption(f"👤 **Maker:** {item.maker}")
        with m2:
            if item.timing_note:
                st.caption(f"⏰ {item.timing_note}")
        with m3:
            new_status = st.selectbox(
                "Status",
                options   = config.STATUS_OPTIONS,
                index     = config.STATUS_OPTIONS.index(item.status) if item.status in config.STATUS_OPTIONS else 0,
                key       = f"sts_{deal.company_name}_{phase}_{item.step_number}",
                label_visibility="collapsed",
            )
            if new_status != item.status:
                item.status = new_status
                ds.update_pipeline_deal(deal.company_name, deal)

        if item.sub_notes or st.session_state.get(f"edit_{deal.company_name}_{phase}_{item.step_number}"):
            with st.expander("📝 Notes"):
                notes = st.text_area(
                    "Notes",
                    value    = item.sub_notes,
                    key      = f"notes_{deal.company_name}_{phase}_{item.step_number}",
                    label_visibility="collapsed",
                    height   = 60,
                )
                if notes != item.sub_notes:
                    item.sub_notes = notes
                    ds.update_pipeline_deal(deal.company_name, deal)
        st.markdown("")


def _generate_pipeline_term_sheet(deal):
    try:
        from term_sheet import TermSheetGenerator
        import tempfile, os

        gen = TermSheetGenerator()
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = tmp.name

        gen.generate_draft_for_pipeline(deal, tmp_path)

        with open(tmp_path, "rb") as f:
            docx_bytes = f.read()
        os.unlink(tmp_path)

        safe = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in deal.company_name)
        st.download_button(
            label     = f"⬇️ Download Draft Term Sheet — {deal.company_name}",
            data      = docx_bytes,
            file_name = f"DraftTermSheet_{safe}.docx",
            mime      = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key       = f"dl_detail_{deal.company_name}",
        )
        st.success("✅ Draft term sheet generated — click above to download.")

    except FileNotFoundError:
        st.warning(f"⚠️ Template not found at: `{config.TERM_SHEET_TEMPLATE}`")
    except Exception as e:
        st.error(f"Error: {e}")


def _render_closure_form(deal, ds):
    st.markdown("## 🎯 Close Deal & Archive")
    st.markdown(f"Fill in final details to close **{deal.company_name}**:")

    with st.form("closure_form"):
        c1, c2 = st.columns(2)
        with c1:
            isin   = st.text_input("ISIN Number *", placeholder="INE123456789", max_chars=12)
            coupon = st.number_input("Coupon Rate (% p.a.) *", min_value=0.0, max_value=25.0,
                                     value=9.0, step=0.01, format="%.2f")
        with c2:
            tenor        = st.number_input("Tenor (Months) *", min_value=1, max_value=120, value=24)
            maturity_date = st.date_input("Maturity Date *", value=deal.funding_date)

        cs, cc = st.columns(2)
        with cs:
            submit = st.form_submit_button("✅ Close Deal & Generate Term Sheet",
                                           type="primary", use_container_width=True)
        with cc:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

        if cancel:
            st.session_state['show_closure_form'] = False
            st.rerun()

        if submit:
            form_data = {'isin': isin, 'coupon': coupon, 'tenor': tenor, 'maturity_date': maturity_date}
            ok, errors = validate_closure_form(form_data)
            if not ok:
                display_error_messages(errors)
            else:
                try:
                    closed = ClosedDeal.from_pipeline_deal(deal, isin.upper(), coupon, tenor, maturity_date)
                    ds.move_to_closed(deal, closed)

                    # Generate and save term sheet
                    try:
                        from term_sheet import TermSheetGenerator
                        folder        = create_company_folder(deal.company_name, config.ISSUANCE_FOLDER)
                        ts_path       = folder / f"TermSheet_{isin.upper()}.docx"
                        gen           = TermSheetGenerator()
                        gen.generate_with_highlights(closed, ts_path)
                        st.success(config.SUCCESS_TERM_SHEET_GENERATED)
                        st.info(f"📄 Term sheet saved to: `{ts_path}`")
                    except Exception as te:
                        st.warning(f"Deal closed but term sheet failed: {te}")

                    st.success(config.SUCCESS_DEAL_CLOSED)
                    st.session_state['show_closure_form'] = False
                    st.session_state['page'] = 'closed_deals'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error closing deal: {e}")


# ══════════════════════════════════════════════════
#  CLOSED DEALS VIEW
# ══════════════════════════════════════════════════

def render_closed_deals():
    st.markdown("## ✅ Closed NCD Deals")
    st.markdown("Archive of successfully completed NCD issuances")

    ds           = DataStore()
    closed_deals = ds.load_closed_deals()

    if not closed_deals:
        st.info("ℹ️ No closed deals yet. Complete pipeline deals to move them here.")
        return

    total_size = sum(d.issuance_size for d in closed_deals)
    avg_coupon = sum(d.coupon for d in closed_deals) / len(closed_deals)
    avg_tenor  = sum(d.tenor for d in closed_deals) / len(closed_deals)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Deals",  len(closed_deals))
    with c2: st.metric("Total Size",   format_amount(total_size))
    with c3: st.metric("Avg Coupon",   format_percentage(avg_coupon))
    with c4: st.metric("Avg Tenor",    f"{int(avg_tenor)} months")

    st.markdown("---")

    # Filters
    all_instruments = list({d.instrument_type for d in closed_deals})
    all_classes     = list({d.asset_class     for d in closed_deals})

    fc1, fc2 = st.columns(2)
    with fc1:
        filter_inst = st.multiselect("Filter by Instrument Type",
                                     options=all_instruments, default=all_instruments)
    with fc2:
        filter_cls  = st.multiselect("Filter by Asset Class / Issuer Type",
                                     options=all_classes, default=all_classes)

    filtered = [d for d in closed_deals
                if d.instrument_type in filter_inst and d.asset_class in filter_cls]

    st.caption(f"Showing **{len(filtered)}** of **{len(closed_deals)}** deals")

    if filtered:
        _render_closed_table(filtered)
    else:
        st.info("No deals match the selected filters.")


def _render_closed_table(deals):
    rows = []
    for d in deals:
        rows.append({
            "Issuer":           d.company_name,
            "Type":             d.instrument_type,
            "FS/EF":            d.issuer_type,
            "Size (₹ Cr)":      d.issuance_size,
            "ISIN":             d.isin,
            "Coupon (%)":       d.coupon,
            "Tenor (Mo.)":      d.tenor,
            "Rating":           d.rating,
            "Issue Date":       format_date(d.funding_date),
            "Maturity Date":    format_date(d.maturity_date),
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width = True,
        hide_index          = True,
        column_config = {
            "Issuer":      st.column_config.TextColumn("Issuer", width="medium"),
            "Size (₹ Cr)": st.column_config.NumberColumn("Size (₹ Cr)", format="%.2f"),
            "Coupon (%)":  st.column_config.NumberColumn("Coupon (%)", format="%.2f"),
            "Tenor (Mo.)": st.column_config.NumberColumn("Tenor", format="%d"),
        },
    )

    st.markdown("---")
    col_csv, col_ts = st.columns(2)
    with col_csv:
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            data       = csv,
            file_name  = f"closed_ncd_deals_{date.today().strftime('%Y%m%d')}.csv",
            mime       = "text/csv",
            use_container_width = True,
        )
    with col_ts:
        if st.button("📂 Generate All Term Sheets (Issuance Folder)",
                     use_container_width=True, type="secondary"):
            _populate_issuance_folder(deals)


def _populate_issuance_folder(deals):
    """Generate term sheets for all closed deals and save to Issuance folder."""
    try:
        from term_sheet import TermSheetGenerator
    except ImportError as e:
        st.error(f"Could not import TermSheetGenerator: {e}")
        return

    if not Path(config.TERM_SHEET_TEMPLATE).exists():
        st.warning(
            f"⚠️ Term sheet template not found.\n"
            f"Please place `Term_Sheet_Template.docx` at `{config.TERM_SHEET_TEMPLATE}`"
        )
        return

    gen     = TermSheetGenerator()
    ok_list = []
    fail_list = []

    progress_bar = st.progress(0, text="Generating term sheets…")
    total = len(deals)

    for idx, deal in enumerate(deals):
        try:
            folder = create_company_folder(deal.company_name, config.ISSUANCE_FOLDER)
            safe   = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in deal.company_name)
            isin   = deal.isin.replace("/", "_").replace(" ", "_") if deal.isin else "NOISN"
            ts_path = folder / f"TermSheet_{safe}_{isin}.docx"
            gen.generate_with_highlights(deal, ts_path)
            ok_list.append(f"✅ {deal.company_name} → `{ts_path.name}`")
        except Exception as e:
            fail_list.append(f"❌ {deal.company_name}: {e}")
        progress_bar.progress((idx + 1) / total, text=f"Processing {deal.company_name}…")

    progress_bar.empty()

    if ok_list:
        st.success(f"Generated {len(ok_list)} term sheet(s) in `{config.ISSUANCE_FOLDER}`")
        for msg in ok_list:
            st.markdown(msg)
    if fail_list:
        st.warning(f"{len(fail_list)} deal(s) failed:")
        for msg in fail_list:
            st.markdown(msg)
