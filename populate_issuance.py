"""
populate_issuance.py
One-time script to generate term sheets for ALL existing closed deals
and save them to the Issuance folder.

Run from Code_Streamlit directory:
    python populate_issuance.py
"""

import sys
from pathlib import Path

# ── ensure imports resolve from this directory ──────────────────
sys.path.insert(0, str(Path(__file__).parent))

import config
from data_store import DataStore
from term_sheet import TermSheetGenerator
from utils import create_company_folder


def main():
    print("=" * 60)
    print("  Issuance Folder Population Script")
    print("=" * 60)

    # ── check template exists ────────────────────────────────────
    if not config.TERM_SHEET_TEMPLATE.exists():
        print(f"\n❌ ERROR: Template not found at:\n   {config.TERM_SHEET_TEMPLATE}")
        print("   Please place Term_Sheet_Template.docx in the Code_Streamlit folder.")
        sys.exit(1)

    print(f"\n✅ Template      : {config.TERM_SHEET_TEMPLATE}")
    print(f"✅ Issuance folder: {config.ISSUANCE_FOLDER}")
    print(f"✅ Data file     : {config.DATA_FILE}")

    # ── load closed deals ────────────────────────────────────────
    ds           = DataStore()
    closed_deals = ds.load_closed_deals()

    if not closed_deals:
        print("\nℹ️  No closed deals found in Excel. Nothing to generate.")
        sys.exit(0)

    print(f"\nFound {len(closed_deals)} closed deal(s):")
    for d in closed_deals:
        print(f"  • {d.company_name} | {d.isin} | ₹{d.issuance_size:,.0f} Cr")

    print(f"\nGenerating term sheets…\n")

    gen      = TermSheetGenerator()
    ok_count = 0
    fail_count = 0

    for deal in closed_deals:
        try:
            folder = create_company_folder(deal.company_name, config.ISSUANCE_FOLDER)
            safe   = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in deal.company_name)
            isin   = (deal.isin.replace("/", "_").replace(" ", "_")
                      if deal.isin and deal.isin not in ("N/A", "") else "NO_ISIN")
            ts_path = folder / f"TermSheet_{safe}_{isin}.docx"

            gen.generate_with_highlights(deal, ts_path)
            print(f"  ✅ {deal.company_name}")
            print(f"     → {ts_path}")
            ok_count += 1

        except Exception as e:
            print(f"  ❌ {deal.company_name}: {e}")
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"  Done — {ok_count} generated, {fail_count} failed.")
    print(f"  Files saved in: {config.ISSUANCE_FOLDER}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
