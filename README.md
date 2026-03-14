# NCD Issuance Tracker

> **Streamlined NCD Issuance Pipeline Management System**  
> Track Non-Convertible Debenture deals from initiation to closure with comprehensive checklist management

## 🎯 Overview

The NCD Issuance Tracker is a Streamlit-based application designed for structured product solution teams to manage NCD issuances efficiently. It provides end-to-end tracking from deal initiation through a 5-phase checklist workflow to deal closure with automated term sheet generation.

### Key Features

- ✅ **Pipeline Dashboard** - Visual overview of all active NCD issuances
- 📋 **5-Phase Checklist** - Structured workflow tracking (Pre-Exec → Depository & Stamping → Documents & EBP → T-Day → Post-Issuance)
- 📊 **Progress Tracking** - Real-time completion percentage for each deal and phase
- ⏰ **T-Day Countdown** - Color-coded alerts for upcoming funding dates
- 🎯 **Deal Closure** - Automated term sheet generation and archival
- 📄 **Term Sheet Auto-Population** - Generate populated Word documents from templates
- 💾 **Excel-Based Storage** - Simple file-based data management (no database required)

## 🏗️ Architecture

```
ncd_tracker/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration and constants
├── requirements.txt                # Python dependencies
│
├── constants/                      # Static definitions
│   ├── checklist_items.py         # 5-phase checklist structure
│   └── field_definitions.py       # Excel column mappings
│
├── data/                          # Data layer
│   ├── data_models.py             # PipelineDeal, ClosedDeal classes
│   └── excel_manager.py           # Excel read/write operations
│
├── documents/                     # Document generation
│   └── term_sheet_generator.py   # Word document population
│
├── ui/                            # UI components
│   ├── dashboard.py               # Main dashboard view
│   ├── new_deal.py                # New deal form
│   ├── deal_detail.py             # Checklist tracking
│   ├── closed_deals.py            # Archive view
│   └── future_scope.py            # Roadmap tab
│
└── utils/                         # Utilities
    ├── formatters.py              # Data formatting
    ├── validators.py              # Input validation
    └── helpers.py                 # Helper functions
```

## 📋 Prerequisites

- Python 3.8 or higher
- Windows OS (for file path compatibility)
- Microsoft Word (optional, for viewing generated term sheets)
- Excel (optional, for viewing data files)

## 🚀 Installation

### 1. Clone or Download

```bash
# If using Git
git clone <repository-url>
cd ncd_tracker

# Or extract the ZIP file to your desired location
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- streamlit==1.31.0
- pandas==2.1.4
- openpyxl==3.1.2
- python-docx==1.1.0
- Pillow==10.2.0
- plotly==5.18.0

### 3. Configure File Paths

Edit `config.py` and update the following paths:

```python
BASE_DIR = Path(r"E:\Personal\Trading_Champion\Projects\Solutions_Execution")
DATA_FILE = BASE_DIR / "Bond_Primary_Deals.xlsx"
TERM_SHEET_TEMPLATE = BASE_DIR / "Term_Sheet_Template.docx"
ISSUANCE_FOLDER = BASE_DIR / "Issuance"
```

**Important:** 
- Update `BASE_DIR` to match your local file structure
- Ensure the Excel file `Bond_Primary_Deals.xlsx` exists at the specified path
- Ensure the Word template `Term_Sheet_Template.docx` exists
- The application will create the `Issuance` folder automatically if it doesn't exist

### 4. Prepare Excel File

The Excel file should have two sheets:

**Sheet 1: "Issuance Pipeline"**
```
Columns: Company Name | Instrument Type | Asset Class | Issuance Size (₹ Cr) | 
         Funding Date (T) | Rating | Security | Checklist Progress | 
         Created Date | Status
```

**Sheet 2: "Closed NCD Deal"**
```
Columns: Company Name | Instrument Type | Asset Class | Issuance Size (₹ Cr) | 
         ISIN | Coupon (% p.a.) | Tenor (Months) | Rating | Security | 
         Funding Date | Maturity Date
```

The application will create these sheets automatically if they don't exist.

## 🎮 Usage

### Starting the Application

```bash
cd ncd_tracker
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Workflow

#### 1. **Create New Deal**
- Click "➕ New Issuance" in sidebar
- Fill in required details:
  - Company Name
  - Instrument Type (Listed/Unlisted NCD)
  - Asset Class (NBFC/Housing Finance/MFI/Corporate)
  - Issuance Size (₹ Crore)
  - Funding Date (T-Day)
  - Credit Rating
  - Security Type
- Click "Create Deal"

#### 2. **Track Progress**
- View deal card on Dashboard
- Click "View Details" to open checklist
- Navigate through 5 phase tabs:
  - 📋 Pre-Exec (14 items)
  - 🏦 Depo & Stamp (7 items)
  - 📝 Docs & EBP (11 items)
  - 💰 T-Day (5 items)
  - 📤 Post (10 items)
- Check off completed items
- Update status (Pending/In Progress/Completed/Blocked)
- Add sub-notes as needed

#### 3. **Close Deal**
- Complete all checklist items (100% progress)
- Click "Mark as Closed & Move to Archive"
- Enter final details:
  - ISIN Number
  - Coupon Rate (%)
  - Tenor (Months)
  - Maturity Date
- Click "Close Deal & Generate Term Sheet"
- Deal moves to Closed Deals archive
- Term sheet auto-generated and saved

#### 4. **View Closed Deals**
- Click "✅ Closed Deals" in sidebar
- View archived deals with filters
- Export to CSV if needed

## 📊 Data Formats

### Amounts
- **Unit:** ₹ Crore
- **Format:** XX,XXX.XX (2 decimal places)
- **Example:** ₹500.00 Cr

### Interest/Coupon
- **Unit:** % per annum
- **Format:** XX.XX (2 decimal places)
- **Example:** 9.75%

### Dates
- **Format:** DD/MM/YYYY
- **Example:** 28/03/2026

### ISIN
- **Format:** 12 characters (IN + 10 alphanumeric)
- **Example:** INE123456789

## 🎨 UI Features

### Dashboard
- Summary statistics (Total, Fully Funded, In Progress, Due ≤7 Days)
- Filter by instrument type (All/Listed/Unlisted)
- Deal cards with:
  - T-day countdown (color-coded: green 15+, orange 8-14, red ≤7 days)
  - Progress bar and percentage
  - Phase-wise step counts

### Checklist Tracking
- Tab-based navigation for 5 phases
- Checkbox toggle for completion
- Status dropdown per item
- Expandable notes section
- Real-time progress updates

### Color Coding
- 🟢 **Green (Normal):** 15+ days to funding
- 🟠 **Orange (Warning):** 8-14 days to funding
- 🔴 **Red (Critical):** ≤7 days to funding

## 🔧 Customization

### Adding Checklist Items

Edit `constants/checklist_items.py`:

```python
CHECKLIST_ITEMS = {
    "Pre-Exec": [
        ("Task Title", "Maker", "Timing Note", Listed_Only_Flag),
        # Add more items...
    ],
    # Other phases...
}
```

### Modifying Dropdown Options

Edit `config.py`:

```python
ASSET_CLASSES = ["NBFC", "Housing Finance", "MFI", "Corporate", "Your_New_Class"]
RATING_OPTIONS = ["AAA", "AA+", ..., "Your_New_Rating"]
```

### Changing Date Format

Edit `config.py`:

```python
DATE_FORMAT = "%d/%m/%Y"  # Change to your preferred format
```

## 📝 Term Sheet Generation

The application uses `Term_Sheet_Template.docx` as a template and populates:

- **Auto-populated fields:**
  - Company name, ISIN, Rating
  - Amounts (converted to words)
  - Dates (funding, maturity)
  - Coupon, Tenor
  - Asset class, Security type

- **Manual fields (highlighted in yellow):**
  - Fields still containing `[PLACEHOLDER]` text
  - Require manual input in Word

## 🚨 Troubleshooting

### Excel File Not Found
```
Error: Excel file not found
Solution: Check file path in config.py → BASE_DIR and DATA_FILE
```

### Import Errors
```
Error: ModuleNotFoundError
Solution: Run 'pip install -r requirements.txt'
```

### Data Not Saving
```
Issue: Changes not persisting
Solution: Check file permissions on Excel file
```

### Term Sheet Not Generating
```
Issue: Term sheet generation fails
Solution: Verify Term_Sheet_Template.docx exists and is not open in Word
```

## 🔮 Future Enhancements (Phase 2)

- 🔐 User authentication and role-based access
- 📧 Email notifications for upcoming T-days
- 📊 Advanced analytics and reporting
- 🔗 API integrations (Google Drive, Calendar)
- 📱 Mobile-responsive design
- 🌙 Dark mode support
- 📋 Regulatory compliance checklists
- 🔄 Version control for documents

See **Future Scope** tab in the application for complete roadmap.

## 📞 Support

**Technical Support:**  
Email: support@tradingchampion.in

**Feature Requests:**  
Use the "Future Scope" tab in the application to submit ideas

## 📄 License

Proprietary - Trading Champion Solutions © 2026

## 🙏 Acknowledgments

Built for the Structured Product Solutions team to streamline NCD issuance workflows.

---

**Version:** 1.0.0  
**Last Updated:** March 14, 2026  
**Status:** Production Ready ✅
