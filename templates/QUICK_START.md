# Quick Start Guide - Set Up Your Own Instance

Follow this guide to create your own expense tracker from scratch.

## Prerequisites

- Python 3.9+ installed
- Google account
- Claude Code CLI (if using the skill)

## Step-by-Step Setup (15 minutes)

### Step 1: Clone/Download Repository

```bash
cd ~/your-projects-folder
# If you have git access:
git clone <repository-url> my-expense-tracker
# Or download and extract the ZIP file

cd my-expense-tracker
```

### Step 2: Create Your Google Sheet

**Method A: Import CSV Templates (Easiest)**

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it "Business Expense Tracker" (or whatever you prefer)
4. Import the first CSV:
   - File → Import → Upload
   - Select `templates/Subscriptions.csv`
   - Import location: "Replace current sheet"
   - Click "Import data"
5. Rename the imported sheet from "Sheet1" to "Subscriptions"
6. Add the second sheet:
   - Click the **+** button at bottom left (Add sheet)
   - File → Import → Upload
   - Select `templates/One-Time_Purchases.csv`
   - Import location: "Insert new sheet(s)"
   - Click "Import data"
7. Rename the new sheet to "One-Time Purchases"
8. *(Optional)* Add the Logs sheet:
   - Click the **+** button
   - File → Import → Upload
   - Select `templates/Logs.csv`
   - Import location: "Insert new sheet(s)"
   - Rename to "Logs"

**Method B: Generate Excel File**

```bash
cd templates
pip install openpyxl
python generate_excel_template.py
```

Then upload `Expense_Tracker_Template.xlsx` to Google Drive and open with Google Sheets.

### Step 3: Get Your Sheet ID

1. Look at your Google Sheet URL:
   ```
   https://docs.google.com/spreadsheets/d/1pwwp2I-9Uuf9Nd3sApN12aE2Y9_Vujm3Spxwz-mBHS4/edit
                                          ↑______________________________________↑
                                          This is your SPREADSHEET_ID
   ```
2. Copy that long ID (between `/d/` and `/edit`)

### Step 4: Set Up Google Cloud OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing):
   - Click project dropdown at top
   - "New Project"
   - Name it "Expense Tracker"
   - Click "Create"
3. Enable the Google Sheets API:
   - Search for "Google Sheets API" in the search bar
   - Click on "Google Sheets API"
   - Click "Enable"
4. Create OAuth credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure consent screen:
     - User Type: External
     - App name: "Expense Tracker"
     - User support email: your email
     - Developer contact: your email
     - Save and Continue through all steps
   - Back to "Create OAuth client ID":
     - Application type: "Desktop app"
     - Name: "Expense Tracker Desktop"
     - Click "Create"
   - Click "Download JSON"
   - Save the file to your project directory (it'll have a long name like `client_secret_123456-abc.apps.googleusercontent.com.json`)

### Step 5: Configure Environment

1. Create a `.env` file in the project root:

```bash
cd ~/your-projects-folder/my-expense-tracker
touch .env
```

2. Edit `.env` and add (replace with your values):

```env
# Your Google Sheet ID from Step 3
GOOGLE_SPREADSHEET_ID=1pwwp2I-9Uuf9Nd3sApN12aE2Y9_Vujm3Spxwz-mBHS4

# Path to your OAuth credentials file from Step 4
GOOGLE_CREDENTIALS_PATH=./client_secret_123456-abc.apps.googleusercontent.com.json

# Optional: Set defaults
DEFAULT_PAYMENT_METHOD=Business Credit Card
DEFAULT_ACCOUNT_EMAIL=your-email@example.com
```

### Step 6: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 7: Test Authentication

Run a test expense to trigger OAuth flow:

```bash
python ingest.py '{"type":"subscription","vendor":"Test","category":"Other","monthly_cost":1}'
```

This will:
1. Open your browser for Google OAuth
2. Ask you to select your Google account
3. Show permissions request (allow access to Google Sheets)
4. Create `token.json` for future use
5. Add a test entry to your Subscriptions sheet

**Check your Google Sheet** - you should see a new row with "Test" vendor!

### Step 8: Try the Claude Code Skill (Optional)

If using Claude Code:

```bash
# Make sure you're in the project directory
cd ~/your-projects-folder/my-expense-tracker

# Activate virtual environment
source venv/bin/activate

# Try adding an expense
/add-expense "Notion Plus $10/mo started today"
```

You should see:
```
✅ Logged to Subscriptions:
• Vendor: Notion
• Category: Productivity
• Plan: Plus
• Cost: $10.00/mo (Monthly)
• Payment: Business Credit Card

Row(s) appended to your Google Sheet.
```

### Step 9: Clean Up Test Data

Go to your Google Sheet and delete the test row(s) you just created.

## You're All Set! 🎉

Now you can start logging real expenses:

### Text Input Examples

```bash
/add-expense "Slack Business+ plan $80/mo annual, started Nov 1, 2023"
/add-expense "Bought a standing desk from IKEA for $599"
/add-expense "GitHub Team $44/month, contract ends Dec 31"
```

### File Input Examples

```bash
/add-expense ~/Downloads/invoice.pdf
/add-expense ~/Desktop/receipt.jpg
```

## Troubleshooting

### "File not found" error for credentials
- Check that the filename in `.env` matches your actual credentials file
- Use absolute path if relative path doesn't work:
  ```env
  GOOGLE_CREDENTIALS_PATH=/Users/yourname/my-expense-tracker/client_secret_....json
  ```

### "Invalid spreadsheet ID"
- Double-check you copied the full ID from the URL
- Make sure there are no extra spaces or quotes in `.env`

### OAuth browser doesn't open
- Manually copy the URL from terminal and paste into browser
- Make sure port 8080 or similar isn't blocked

### "Sheet not found" error
- Verify sheet names are exactly: "Subscriptions" and "One-Time Purchases"
- Check for extra spaces in tab names

### Skill not found
- Make sure `.claude/skills/add-expense/SKILL.md` exists
- Restart Claude Code to reload skills

### Formulas not working in Google Sheets
- CSV import may not preserve formulas
- See `templates/STRUCTURE_REFERENCE.md` for manual formula setup
- Or use the Excel import method instead

## Next Steps

1. **Set up formulas**: See `templates/TEMPLATE_README.md` for auto-calculated columns
2. **Add data validation**: Create dropdown menus for categories
3. **Apply conditional formatting**: Highlight expiring subscriptions
4. **Customize categories**: Edit `config.py` to add your own categories
5. **Set defaults**: Update `.env` with your preferred payment method and email

## Resources

- `templates/TEMPLATE_README.md` - Complete setup guide with formulas
- `templates/STRUCTURE_REFERENCE.md` - Visual column reference
- `README.md` - Full project documentation
- `.claude/skills/add-expense/SKILL.md` - Skill configuration

## Support

If you run into issues:
1. Check the troubleshooting section above
2. Review error messages carefully
3. Verify all file paths in `.env` are correct
4. Make sure virtual environment is activated (`source venv/bin/activate`)

Happy expense tracking! 📊
