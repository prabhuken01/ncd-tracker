"""
NCD Tracker - Closed Deals UI
View for archived/completed NCD deals
"""

import streamlit as st
import pandas as pd
import config
from data.excel_manager import ExcelManager
from utils.formatters import *

def render_closed_deals():
    """Render closed deals view"""
    
    st.markdown("## ✅ Closed NCD Deals")
    st.markdown("Archive of successfully completed NCD issuances")
    
    # Load closed deals
    excel_mgr = ExcelManager()
    closed_deals = excel_mgr.load_closed_deals()
    
    if not closed_deals:
        st.info("ℹ️ No closed deals yet. Complete pipeline deals to move them here.")
        return
    
    # Summary stats
    total_size = sum(deal.issuance_size for deal in closed_deals)
    avg_coupon = sum(deal.coupon for deal in closed_deals) / len(closed_deals) if closed_deals else 0
    avg_tenor = sum(deal.tenor for deal in closed_deals) / len(closed_deals) if closed_deals else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Deals", len(closed_deals))
    with col2:
        st.metric("Total Size", format_amount(total_size))
    with col3:
        st.metric("Avg Coupon", format_percentage(avg_coupon))
    with col4:
        st.metric("Avg Tenor", f"{int(avg_tenor)} months")
    
    st.markdown("---")
    
    # Filters
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        filter_instrument = st.multiselect(
            "Filter by Instrument Type",
            options=config.INSTRUMENT_TYPES,
            default=config.INSTRUMENT_TYPES
        )
    with col_filter2:
        filter_asset = st.multiselect(
            "Filter by Asset Class",
            options=config.ASSET_CLASSES,
            default=config.ASSET_CLASSES
        )
    
    # Filter deals
    filtered_deals = [
        deal for deal in closed_deals
        if deal.instrument_type in filter_instrument and deal.asset_class in filter_asset
    ]
    
    st.caption(f"Showing {len(filtered_deals)} of {len(closed_deals)} deals")
    
    # Display as table
    if filtered_deals:
        render_deals_table(filtered_deals)
    else:
        st.info("No deals match the selected filters")

def render_deals_table(deals):
    """Render deals in a table format"""
    
    # Convert to DataFrame
    data = []
    for deal in deals:
        data.append({
            "Company": deal.company_name,
            "Type": deal.instrument_type,
            "Asset Class": deal.asset_class,
            "Size (₹ Cr)": deal.issuance_size,
            "ISIN": deal.isin,
            "Coupon (%)": deal.coupon,
            "Tenor (Months)": deal.tenor,
            "Rating": deal.rating,
            "Funding Date": format_date(deal.funding_date),
            "Maturity Date": format_date(deal.maturity_date),
        })
    
    df = pd.DataFrame(data)
    
    # Display with custom formatting
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Company": st.column_config.TextColumn("Company Name", width="medium"),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Size (₹ Cr)": st.column_config.NumberColumn("Size (₹ Cr)", format="%.2f"),
            "Coupon (%)": st.column_config.NumberColumn("Coupon (%)", format="%.2f"),
            "Tenor (Months)": st.column_config.NumberColumn("Tenor", format="%d"),
        }
    )
    
    # Export options
    st.markdown("---")
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name=f"closed_ncd_deals_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_export2:
        # Excel export
        st.info("💡 Excel data is available at the source file")
        st.caption(f"Path: {config.DATA_FILE}")
