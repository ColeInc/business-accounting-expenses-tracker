# Google Sheets Template for Business Expense Tracker

This directory contains CSV templates that define the structure of the Google Sheets used by the expense tracker.

## Quick Start

1. Create a new Google Sheet
2. Import each CSV file as a separate tab (sheet):
   - `Subscriptions.csv` → "Subscriptions" tab
   - `One-Time_Purchases.csv` → "One-Time Purchases" tab
   - `Logs.csv` → "Logs" tab (will be auto-created on first use if missing)
3. Copy your Google Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`
4. Update your `.env` file with: `GOOGLE_SPREADSHEET_ID=YOUR_SHEET_ID`

## Sheet Structure

### Subscriptions Tab (Columns A-P)

Tracks recurring subscription expenses with auto-renewal tracking.

| Column | Name | Type | Auto-Calculated | Description |
|--------|------|------|-----------------|-------------|
| A | Vendor | Text | No | Service provider name (e.g., "Notion", "Slack") |
| B | Category | Dropdown | No | See valid categories below |
| C | Plan Tier | Text | No | Subscription tier (e.g., "Plus", "Business+") |
| D | Billing Cycle | Dropdown | No | Monthly, Annual, or Quarterly |
| E | Monthly Cost | Number | No | Monthly cost in dollars |
| F | Annual Cost | Number | **YES** | Formula: `=E*12` |
| G | Start Date | Date | No | When subscription started (YYYY-MM-DD) |
| H | Next Renewal | Date | **YES** | Formula: `=IF(D="Monthly",DATE(YEAR(G),MONTH(G)+1,DAY(G)),IF(D="Annual",DATE(YEAR(G)+1,MONTH(G),DAY(G)),DATE(YEAR(G),MONTH(G)+3,DAY(G))))` |
| I | Days Until Renewal | Number | **YES** | Formula: `=H-TODAY()` |
| J | Auto Renew | Text | No | "Yes" or "No" |
| K | Payment Method | Text | No | How subscription is paid (e.g., "Business Credit Card") |
| L | Account Email | Email | No | Email address used for account |
| M | Contract End | Date | No | Contract end date if applicable |
| N | Cancellation Notice Days | Number | No | Days notice required before cancellation |
| O | Cancel By Date | Date | **YES** | Formula: `=M-N` (only if Contract End exists) |
| P | Notes | Text | No | Additional notes |

**Valid Subscription Categories:**
- Accounting
- Analytics
- Communication
- CRM
- Design
- Development
- Hosting
- Legal
- Marketing
- Payroll
- Productivity
- Project Mgmt
- Security
- Storage
- Other

### One-Time Purchases Tab (Columns A-J)

Tracks single purchase expenses.

| Column | Name | Type | Description |
|--------|------|------|-------------|
| A | Item | Text | Item or service purchased |
| B | Category | Dropdown | See valid categories below |
| C | Vendor | Text | Where purchased from |
| D | Purchase Date | Date | Date of purchase (YYYY-MM-DD) |
| E | Amount | Number | Purchase amount in dollars |
| F | Payment Method | Text | How purchase was paid |
| G | Tax Deductible | Text | "Yes" or "No" |
| H | Receipt Saved | Text | "Yes" or "No" |
| I | Warranty Until | Date | Warranty expiration date if applicable |
| J | Notes | Text | Additional notes |

**Valid One-Time Categories:**
- Branding
- Equipment
- Furniture
- Legal Fees
- Licenses
- Office Supplies
- Software License
- Training
- Web
- Other

### Logs Tab (Columns A-E)

Auto-generated audit trail when processing expenses from files (PDFs/images).

| Column | Name | Type | Description |
|--------|------|------|-------------|
| A | Invoice Name | Text | Filename of the processed invoice/receipt |
| B | Date/Time (NZT) | DateTime | When the expense was processed (New Zealand Time) |
| C | Description | Text | Summary of the expense |
| D | Recurring? | Text | "Yes" or "No" |
| E | Sheet Appended | Text | Which sheet it was added to ("Subscriptions" or "One-Time Purchases") |

**Note:** The Logs tab is automatically created when you first process a file-based expense. You can delete the example entries or leave them as reference.

## Setting Up Formulas in Google Sheets

### For Subscriptions Tab

After importing the CSV, the formulas should work automatically. If you're creating the sheet manually:

1. **Annual Cost (Column F):**
   - In F2: `=E2*12`
   - Copy down for all rows

2. **Next Renewal (Column H):**
   - In H2: `=IF(D2="Monthly",DATE(YEAR(G2),MONTH(G2)+1,DAY(G2)),IF(D2="Annual",DATE(YEAR(G2)+1,MONTH(G2),DAY(G2)),DATE(YEAR(G2),MONTH(G2)+3,DAY(G2))))`
   - Copy down for all rows

3. **Days Until Renewal (Column I):**
   - In I2: `=H2-TODAY()`
   - Copy down for all rows

4. **Cancel By Date (Column O):**
   - In O2: `=IF(M2="","",M2-N2)`
   - Copy down for all rows

### Conditional Formatting (Optional)

To highlight subscriptions that need attention:

1. **Expiring Soon** (Days Until Renewal < 30):
   - Select column I
   - Format → Conditional formatting
   - Format cells if: Custom formula is `=I2<30`
   - Background: Light orange

2. **Auto-Renew Off** (Requires manual renewal):
   - Select column J
   - Format → Conditional formatting
   - Format cells if: Text contains "No"
   - Background: Light yellow

## Example Data

The CSV files include 3 example entries each:

**Subscriptions:**
- Notion Plus ($10/mo, Monthly)
- Slack Business+ ($80/mo, Annual)
- GitHub Team ($44/mo, Monthly)

**One-Time Purchases:**
- Standing Desk ($599)
- Ergonomic Mouse ($89.99)
- Adobe Stock Photos ($249)

**Logs:**
- Three sample log entries showing processed invoices

Feel free to delete the example rows after understanding the structure.

## Data Validation (Optional)

To add dropdown menus for categories:

### Subscriptions Categories (Column B)
1. Select column B (starting from B2)
2. Data → Data validation
3. Criteria: List of items
4. Items: `Accounting,Analytics,Communication,CRM,Design,Development,Hosting,Legal,Marketing,Payroll,Productivity,Project Mgmt,Security,Storage,Other`

### Billing Cycle (Column D)
1. Select column D (starting from D2)
2. Data → Data validation
3. Criteria: List of items
4. Items: `Monthly,Annual,Quarterly`

### One-Time Categories (Column B in One-Time Purchases)
1. Select column B (starting from B2)
2. Data → Data validation
3. Criteria: List of items
4. Items: `Branding,Equipment,Furniture,Legal Fees,Licenses,Office Supplies,Software License,Training,Web,Other`

## Sharing & Permissions

To use with the expense tracker:
1. Keep the sheet private to your Google account
2. The OAuth flow will request permission to access this specific spreadsheet
3. No need to share the sheet publicly

## Troubleshooting

**Formulas not calculating?**
- Ensure dates are formatted as dates (Format → Number → Date)
- Check that billing cycle values match exactly: "Monthly", "Annual", or "Quarterly"

**Import issues?**
- Google Sheets may not preserve formulas when importing CSV
- You may need to manually add formulas after importing (see "Setting Up Formulas" above)

**Logs tab missing?**
- The Logs tab is created automatically when you first process a file-based expense
- You can manually create it using the Logs.csv template if needed

## Next Steps

After setting up your Google Sheet:
1. Update `.env` with your `GOOGLE_SPREADSHEET_ID`
2. Run `/add-expense "Test expense $5"` to verify the integration works
3. Check that the expense appears in the appropriate tab
