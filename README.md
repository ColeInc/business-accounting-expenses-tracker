# Business Expense Tracker

A natural language expense tracker that logs business expenses to Google Sheets using Claude Code.

## Features

- 📝 Natural language input - just describe your expense
- 🔄 Handles recurring subscriptions and one-time purchases
- 📊 Automatically categorizes and validates expenses
- ☁️ Syncs directly to Google Sheets
- 🚀 No API key required - uses Claude Code's built-in Claude access

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Google Sheets

1. Obtain OAuth credentials from Google Cloud Console
2. Save credentials JSON file to project directory
3. Update `.env` with your settings:

```env
GOOGLE_SPREADSHEET_ID=your-sheet-id-here
GOOGLE_CREDENTIALS_PATH=./your-credentials-file.json
DEFAULT_PAYMENT_METHOD=Business Credit Card
DEFAULT_ACCOUNT_EMAIL=your-email@example.com
```

### 3. First Run OAuth Flow

On first use, you'll be prompted to authenticate with Google:
```bash
source venv/bin/activate
python ingest.py '{"type":"subscription","vendor":"Test","category":"Other","monthly_cost":1}'
```

This creates `token.json` for future use.

## Usage

### With Claude Code (Recommended)

Simply invoke the skill:

```
/add-expense Notion Plus $10/mo started today
/add-expense Bought a Dell monitor for $599
/add-expense Log: Slack Pro $8/mo, wireless keyboard $89
```

The skill will:
1. Parse your natural language input
2. Extract expense details into structured data
3. Validate and categorize the expense
4. Add it to your Google Sheet
5. Show you a confirmation summary

### Direct Python Usage (Advanced)

You can also call `ingest.py` directly with pre-formatted JSON:

```bash
echo '{"type":"subscription","vendor":"Notion","category":"Productivity","monthly_cost":10}' | python ingest.py --stdin
```

## Expense Types

### Subscriptions

Recurring expenses tracked with:
- Vendor, category, plan tier
- Billing cycle (Monthly/Annual/Quarterly)
- Monthly cost (auto-calculated if annual/quarterly)
- Start date, renewal status
- Contract end date, cancellation notice period

**Valid Categories:** Accounting, Analytics, Communication, CRM, Design, Development, Hosting, Legal, Marketing, Payroll, Productivity, Project Mgmt, Security, Storage, Other

### One-Time Purchases

Single purchases tracked with:
- Item name, category, vendor
- Purchase date and amount
- Payment method
- Tax deductible status
- Receipt saved, warranty info

**Valid Categories:** Branding, Equipment, Furniture, Legal Fees, Licenses, Office Supplies, Software License, Training, Web, Other

## Project Structure

```
├── .claude/
│   └── skills/
│       └── add-expense/
│           └── SKILL.md          # Claude Code skill definition
├── config.py                     # Configuration and categories
├── ingest.py                     # Main ingestion script
├── validator.py                  # Data validation logic
├── sheets.py                     # Google Sheets API client
├── models.py                     # Data models
├── utils.py                      # Utility functions
├── requirements.txt              # Python dependencies
└── .env                          # Environment configuration
```

## Architecture

**Flow:**
```
User → Claude Code Skill → Parse to JSON → ingest.py → Validate → Google Sheets
```

**Benefits:**
- No separate Anthropic API key needed
- Uses Claude Code's subscription
- Simpler setup process
- Native skill integration

## Examples

**Simple subscription:**
```
/add-expense GitHub Team plan $4 per user monthly
```

**One-time purchase:**
```
/add-expense Bought standing desk from IKEA for $299 on 3/10
```

**Multiple expenses:**
```
/add-expense Log today's expenses: Figma Pro $15/mo, MacBook charger $79
```

**Detailed subscription:**
```
/add-expense Salesforce Enterprise plan $150/mo annual contract ending 12/31/2026, 30 day cancellation notice
```

## Troubleshooting

**OAuth errors:**
- Delete `token.json` and re-authenticate
- Check credentials file path in `.env`
- Verify Google Sheets API is enabled

**Validation errors:**
- Check category names match valid options
- Ensure dates are in MM/DD/YYYY format
- Verify billing cycle is Monthly/Annual/Quarterly

**Skill not found:**
- Restart Claude Code to reload skills
- Check `.claude/skills/add-expense/SKILL.md` exists
- Verify YAML frontmatter is correctly formatted

## License

MIT
