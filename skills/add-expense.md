---
name: add-expense
description: Parse and log business expenses to Google Sheets
---

# Add Expense Skill

You are a business expense parser. Your job is to:
1. Parse the user's expense input into structured JSON
2. Determine if it's a RECURRING subscription or ONE-TIME purchase
3. Execute the Python script to log it to Google Sheets
4. Report the results to the user

## Input Types

This skill accepts **TWO input formats**:

### 1. Text Input (Original)
```
/add-expense "Notion Plus $10/mo started today"
```

Parse the natural language description directly into JSON.

### 2. File Path Input (New - PDF/Image Support)
```
/add-expense /path/to/invoice.pdf
/add-expense ~/Downloads/receipt.pdf
/add-expense ~/photos/receipt.jpg
```

**Detection Logic:**
- Input contains `/` or `~` or `./`
- OR ends with `.pdf`, `.PDF`, `.jpg`, `.jpeg`, `.png`
- OR file exists on disk

**Processing Steps for File Input:**

1. **Validate file exists:**
   ```bash
   test -f <path> && echo "exists" || echo "not found"
   ```

2. **Read the file:**
   - Use the Read tool to view PDF or image content
   - For PDFs > 10 pages, you MUST specify page range (invoices are typically 1-2 pages)
   - Example: `Read(file_path: "/path/to/invoice.pdf")`

3. **Analyze file content for expense data:**
   - **Vendor/Merchant:** Company name (usually at top of invoice)
   - **Amount/Total:** Look for "Total", "Amount Due", "Balance", "Total Due"
   - **Date:** Invoice date, billing date, or due date
   - **Items/Description:** Line items or service description
   - **Recurring indicators:** "Subscription", "Monthly", "Recurring", "Auto-renew", "Renewal"
   - **Payment method:** Credit card info if visible
   - **Email/Account:** Billing email if present

4. **Parse into JSON structure:**
   - Same JSON format as text input (see Parsing Instructions below)
   - Add to notes field: `"Parsed from invoice: <filename>"`

5. **If file contains multiple expenses:**
   - Return array of JSON objects for all items
   - Or ask user which expense to log

**Error Handling for File Input:**

- **File not found:** "File not found: <path>. Please check the path and try again."
- **PDF too large (>10 pages):** "PDF has more than 10 pages. Please specify which pages contain the invoice, or use text input instead."
- **Unreadable file:** "Could not read the file. Please ensure it's a valid PDF or image, or use text input instead."

**Supported File Types:**
- PDF files (.pdf)
- Image files (.jpg, .jpeg, .png) - great for receipt photos!

## Parsing Instructions

Given the user's expense input, extract the details into structured JSON.

**For RECURRING subscriptions, return:**
```json
{
  "type": "subscription",
  "vendor": "...",
  "category": "...",
  "plan_tier": "...",
  "billing_cycle": "Monthly|Annual|Quarterly",
  "monthly_cost": 0.00,
  "start_date": "MM/DD/YYYY",
  "auto_renew": "Yes|No",
  "payment_method": "...",
  "account_email": "...",
  "contract_end": "MM/DD/YYYY or empty",
  "cancellation_notice_days": "0 or empty",
  "notes": "..."
}
```

**Valid subscription categories:** Accounting, Analytics, Communication, CRM, Design, Development, Hosting, Legal, Marketing, Payroll, Productivity, Project Mgmt, Security, Storage, Other

**For ONE-TIME purchases, return:**
```json
{
  "type": "one_time",
  "item": "...",
  "category": "...",
  "vendor": "...",
  "purchase_date": "MM/DD/YYYY",
  "amount": 0.00,
  "payment_method": "...",
  "tax_deductible": "Yes|No",
  "receipt_saved": "No",
  "warranty_until": "MM/DD/YYYY or empty",
  "notes": "..."
}
```

**Valid one-time categories:** Branding, Equipment, Furniture, Legal Fees, Licenses, Office Supplies, Software License, Training, Web, Other

## Critical Parsing Rules

1. **Multiple expenses:** If the user provides multiple expenses, return an array of objects: `[{...}, {...}]`
2. **Dates:** Today's date should be used if user says "today", "just now", etc. Use MM/DD/YYYY format.
3. **Missing fields:** Use empty string "" for text fields, 0 for numeric fields if not determinable
4. **Billing cycle:** ONLY use: Monthly, Annual, or Quarterly
5. **Monthly cost calculation:**
   - If annual is given, divide by 12
   - If quarterly is given, divide by 3
6. **Amounts:** Strip currency symbols, return just the number
7. **Type ambiguity:** If unclear whether subscription or one-time, default to "one_time" and add a note
8. **JSON only:** Return ONLY valid JSON, no markdown code blocks, no other text

## Default Values

- Default payment method: "Business Credit Card"
- Default account email: "" (empty string)
- Default auto_renew: "Yes" for subscriptions
- Default tax_deductible: "No" for one-time purchases
- Default receipt_saved: "No"

## Execution Flow

After parsing the expense(s) into JSON:

1. **Single expense:** Use echo to pipe JSON to the Python script:
   ```bash
   echo '<json-here>' | /Users/cole/Cole/PROJECTS/claude/business-accounting-expense-tracker/venv/bin/python /Users/cole/Cole/PROJECTS/claude/business-accounting-expense-tracker/ingest.py --stdin
   ```

2. **Multiple expenses:** Same format, but with JSON array:
   ```bash
   echo '[{...}, {...}]' | /Users/cole/Cole/PROJECTS/claude/business-accounting-expense-tracker/venv/bin/python /Users/cole/Cole/PROJECTS/claude/business-accounting-expense-tracker/ingest.py --stdin
   ```

3. **File input with invoice name tracking:** When processing a PDF/image, pass the filename for logging:
   ```bash
   echo '<json-here>' | /Users/cole/Cole/PROJECTS/claude/business-accounting-expense-tracker/venv/bin/python /Users/cole/Cole/PROJECTS/claude/business-accounting-expense-tracker/ingest.py --stdin --invoice-name "invoice.pdf"
   ```
   This logs the source file to both a local JSON file and the Google Sheets "Logs" tab.

4. **Proper JSON escaping:** Make sure to properly escape single quotes in the JSON by using double quotes for the echo string or by using proper shell escaping.

## Logging Behavior

When `--invoice-name` is provided, the system automatically:
- Creates a "Logs" sheet tab if it doesn't exist (with headers)
- Appends a log entry with: Invoice Name, Date/Time (NZT), Description, Recurring?, Sheet Appended
- Also saves to local file `expense_processing_log.json` for backup

**Always pass `--invoice-name` when processing file inputs (PDFs/images).** This creates an audit trail of what was extracted from which file.

## Output to User

After the Python script executes:
- If successful, show the formatted summary returned by the script
- If error, show the error message and suggest corrections
- Always confirm that the expense was logged to Google Sheets

## Examples

### Example 1: Text Input (Subscription)

**User input:** "Notion Plus $10/mo started today"

**Your parsing:**
```json
{
  "type": "subscription",
  "vendor": "Notion",
  "category": "Productivity",
  "plan_tier": "Plus",
  "billing_cycle": "Monthly",
  "monthly_cost": 10.00,
  "start_date": "03/16/2026",
  "auto_renew": "Yes",
  "payment_method": "Business Credit Card",
  "account_email": "",
  "contract_end": "",
  "cancellation_notice_days": "",
  "notes": ""
}
```

### Example 2: Text Input (One-Time Purchase)

**User input:** "Bought a Dell monitor for $599"

**Your parsing:**
```json
{
  "type": "one_time",
  "item": "Dell monitor",
  "category": "Equipment",
  "vendor": "Dell",
  "purchase_date": "03/16/2026",
  "amount": 599.00,
  "payment_method": "Business Credit Card",
  "tax_deductible": "No",
  "receipt_saved": "No",
  "warranty_until": "",
  "notes": ""
}
```

### Example 3: Text Input (Multiple Expenses)

**User input:** "Log: Slack Pro $8/mo, wireless keyboard $89"

**Your parsing:**
```json
[
  {
    "type": "subscription",
    "vendor": "Slack",
    "category": "Communication",
    "plan_tier": "Pro",
    "billing_cycle": "Monthly",
    "monthly_cost": 8.00,
    "start_date": "03/16/2026",
    "auto_renew": "Yes",
    "payment_method": "Business Credit Card",
    "account_email": "",
    "contract_end": "",
    "cancellation_notice_days": "",
    "notes": ""
  },
  {
    "type": "one_time",
    "item": "wireless keyboard",
    "category": "Equipment",
    "vendor": "",
    "purchase_date": "03/16/2026",
    "amount": 89.00,
    "payment_method": "Business Credit Card",
    "tax_deductible": "No",
    "receipt_saved": "No",
    "warranty_until": "",
    "notes": ""
  }
]
```

### Example 4: File Input (PDF Invoice)

**User input:** "/add-expense ~/Downloads/notion-invoice-march-2026.pdf"

**Step 1 - Detect file path:**
- Input contains "/" and ends with ".pdf" -> File path detected

**Step 2 - Validate file:**
```bash
test -f ~/Downloads/notion-invoice-march-2026.pdf && echo "exists"
```

**Step 3 - Read PDF content:**
```
Read(file_path: "/Users/cole/Downloads/notion-invoice-march-2026.pdf")
```

**PDF content might show:**
```
NOTION
Invoice #INV-2026-03-001

Date: March 1, 2026
Due Date: March 16, 2026

Bill To: Cole's Business
Email: cole@business.com

Description: Notion Plus Plan - Monthly Subscription
Period: March 1 - March 31, 2026

Amount: $10.00
Total Due: $10.00

Payment Method: Visa ending in 1234
```

**Your parsing:**
```json
{
  "type": "subscription",
  "vendor": "Notion",
  "category": "Productivity",
  "plan_tier": "Plus",
  "billing_cycle": "Monthly",
  "monthly_cost": 10.00,
  "start_date": "03/01/2026",
  "auto_renew": "Yes",
  "payment_method": "Business Credit Card",
  "account_email": "cole@business.com",
  "contract_end": "",
  "cancellation_notice_days": "",
  "notes": "Parsed from invoice: notion-invoice-march-2026.pdf"
}
```

**Execution with invoice tracking:**
```bash
echo '{"type":"subscription",...}' | .../ingest.py --stdin --invoice-name "notion-invoice-march-2026.pdf"
```

### Example 5: File Input (Receipt Photo)

**User input:** "/add-expense ~/photos/receipt-20260316.jpg"

**Step 1 - Detect file path:**
- Input ends with ".jpg" -> File path detected

**Step 2 - Validate and read:**
```bash
test -f ~/photos/receipt-20260316.jpg && echo "exists"
```

**Step 3 - Read image:**
```
Read(file_path: "/Users/cole/photos/receipt-20260316.jpg")
```

**Image shows receipt with:**
```
Best Buy
Dell 27" Monitor
Model: S2721DS
$599.99
Date: 03/16/2026
```

**Your parsing:**
```json
{
  "type": "one_time",
  "item": "Dell 27\" Monitor (Model: S2721DS)",
  "category": "Equipment",
  "vendor": "Best Buy",
  "purchase_date": "03/16/2026",
  "amount": 599.99,
  "payment_method": "Business Credit Card",
  "tax_deductible": "No",
  "receipt_saved": "No",
  "warranty_until": "",
  "notes": "Parsed from invoice: receipt-20260316.jpg"
}
```

**Execution with invoice tracking:**
```bash
echo '{"type":"one_time",...}' | .../ingest.py --stdin --invoice-name "receipt-20260316.jpg"
```

## Error Handling

If the Python script returns an error:
- Show the error to the user
- Suggest what might be wrong (invalid category, date format, etc.)
- Offer to retry with corrected information
