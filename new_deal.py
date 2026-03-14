"""
NCD Tracker - New Deal Form UI
Form for creating new NCD issuance deals
"""

import streamlit as st
from datetime import date, timedelta
import config
from data.excel_manager import ExcelManager
from data.data_models import PipelineDeal
from utils.validators import validate_new_deal_form
from utils.helpers import display_error_messages, display_success_message

def render_new_deal_form():
    """Render new deal initiation form"""
    
    st.markdown("## 📝 New Issuance - Deal Initiation")
    st.markdown("Complete the form below to create a new NCD issuance in the pipeline.")
    
    with st.form("new_deal_form"):
        # Company Name
        company_name = st.text_input(
            "Company Name *",
            help=config.TOOLTIPS['company_name'],
            placeholder="Enter full legal name of issuer"
        )
        
        # Row 1: Instrument Type and Asset Class
        col1, col2 = st.columns(2)
        with col1:
            instrument_type = st.selectbox(
                "Instrument Type *",
                options=config.INSTRUMENT_TYPES,
                help=config.TOOLTIPS['instrument_type']
            )
        with col2:
            asset_class = st.selectbox(
                "Asset Class *",
                options=config.ASSET_CLASSES,
                help=config.TOOLTIPS['asset_class']
            )
        
        # Row 2: Issuance Size and Funding Date
        col3, col4 = st.columns(2)
        with col3:
            issuance_size = st.number_input(
                f"Issuance Size ({config.AMOUNT_UNIT}) *",
                min_value=float(config.MIN_ISSUANCE_SIZE),
                max_value=float(config.MAX_ISSUANCE_SIZE),
                value=100.0,
                step=10.0,
                format="%.2f",
                help=config.TOOLTIPS['issuance_size']
            )
        with col4:
            # Default to 30 days from today
            default_date = date.today() + timedelta(days=30)
            funding_date = st.date_input(
                "Funding Date (T-Day) *",
                value=default_date,
                min_value=date.today() - timedelta(days=90),
                max_value=date.today() + timedelta(days=365),
                help=config.TOOLTIPS['funding_date'],
                format=config.DATE_INPUT_FORMAT
            )
        
        # Row 3: Rating and Security
        col5, col6 = st.columns(2)
        with col5:
            rating = st.selectbox(
                "Credit Rating *",
                options=config.RATING_OPTIONS,
                help=config.TOOLTIPS['rating']
            )
        with col6:
            security = st.selectbox(
                "Security Type *",
                options=config.SECURITY_TYPES,
                help=config.TOOLTIPS['security']
            )
        
        # Required fields note
        st.caption("* Required fields")
        
        # Submit buttons
        col_submit, col_cancel = st.columns([1, 1])
        with col_submit:
            submit = st.form_submit_button("✅ Create Deal", use_container_width=True, type="primary")
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state['page'] = 'dashboard'
            st.rerun()
        
        if submit:
            # Collect form data
            form_data = {
                'company_name': company_name,
                'instrument_type': instrument_type,
                'asset_class': asset_class,
                'issuance_size': issuance_size,
                'funding_date': funding_date,
                'rating': rating,
                'security': security
            }
            
            # Validate
            is_valid, errors = validate_new_deal_form(form_data)
            
            if not is_valid:
                st.error("⚠️ Please fix the following errors:")
                display_error_messages(errors)
            else:
                # Check for duplicate
                excel_mgr = ExcelManager()
                if excel_mgr.company_exists(company_name):
                    st.error(config.ERROR_DUPLICATE_ENTRY)
                else:
                    # Create deal
                    try:
                        # Initialize checklist
                        checklists = excel_mgr.initialize_checklist_for_deal(instrument_type)
                        
                        # Create deal object
                        new_deal = PipelineDeal(
                            company_name=company_name,
                            instrument_type=instrument_type,
                            asset_class=asset_class,
                            issuance_size=issuance_size,
                            funding_date=funding_date,
                            rating=rating,
                            security=security,
                            checklists=checklists,
                            created_date=date.today(),
                            status="In Progress"
                        )
                        
                        # Update progress string
                        new_deal.update_checklist_progress()
                        
                        # Save to Excel
                        excel_mgr.save_pipeline_deal(new_deal)
                        
                        # Success
                        st.success(config.SUCCESS_DEAL_CREATED)
                        st.balloons()
                        
                        # Navigate to deal detail
                        st.session_state['selected_deal'] = company_name
                        st.session_state['page'] = 'deal_detail'
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error creating deal: {str(e)}")

def render_info_panel():
    """Render information panel"""
    with st.sidebar:
        st.markdown("### ℹ️ Deal Initiation Guide")
        
        st.markdown("""
        **Required Information:**
        - Company legal name
        - NCD type (Listed/Unlisted)
        - Business category
        - Deal size in Rs Crore
        - Target funding date
        - Credit rating
        - Security/collateral type
        
        **Next Steps:**
        After creating the deal, you'll be taken to the checklist tracker to monitor pre-funding activities across 5 phases.
        """)
        
        st.markdown("---")
        st.caption("💡 Tip: All deals start with 'In Progress' status and progress to 'Fully Funded' when all checklist items are completed.")
