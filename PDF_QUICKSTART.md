# PDF/Image Support - Quick Start Guide

## 🎉 Your `/add-expense` skill now accepts PDF invoices and receipt photos!

## Quick Examples

### PDF Invoice
```bash
/add-expense ~/Downloads/notion-invoice.pdf
```

### Receipt Photo
```bash
/add-expense ~/photos/receipt.jpg
```

### Text (Still Works!)
```bash
/add-expense "Notion $10/mo started today"
```

## How to Use

### Step 1: Save Your Invoice/Receipt

Save your invoice or receipt to any location on your computer:
- `~/Downloads/` (default download location)
- `~/Documents/invoices/`
- `~/Desktop/`
- Or any other folder

Supported formats:
- PDF files (`.pdf`)
- Image files (`.jpg`, `.jpeg`, `.png`)

### Step 2: Run the Command

```bash
/add-expense /path/to/your/invoice.pdf
```

Or use relative paths:
```bash
/add-expense ~/Downloads/invoice.pdf
/add-expense ./receipt.jpg
```

### Step 3: Review & Confirm

The skill will:
1. ✅ Read your PDF/image
2. ✅ Extract expense details automatically
3. ✅ Determine if it's a subscription or one-time purchase
4. ✅ Log it to Google Sheets
5. ✅ Show you a confirmation

## What Gets Extracted

The skill automatically finds:

| Field | What It Looks For |
|-------|------------------|
| **Vendor** | Company name at top of invoice |
| **Amount** | "Total", "Amount Due", "Balance" |
| **Date** | Invoice date or billing date |
| **Description** | Service name or item description |
| **Subscription?** | Keywords: "Subscription", "Monthly", "Recurring", "Auto-renew" |
| **Email** | Billing email if visible |
| **Payment Method** | Credit card info if shown |

## Real-World Examples

### Example 1: Monthly SaaS Invoice

**Your invoice (PDF) shows:**
```
NOTION
Invoice Date: March 1, 2026
Notion Plus Plan - Monthly Subscription
Total: $10.00
```

**Command:**
```bash
/add-expense ~/Downloads/notion-march-2026.pdf
```

**Result:**
- Logged to "Subscriptions" tab
- Vendor: Notion
- Monthly Cost: $10.00
- Billing Cycle: Monthly
- Auto-Renew: Yes
- Notes: "Parsed from invoice: notion-march-2026.pdf"

### Example 2: Equipment Purchase Receipt

**Your receipt (photo) shows:**
```
Best Buy
Dell 27" Monitor
$599.99
Date: 03/16/2026
```

**Command:**
```bash
/add-expense ~/photos/bestbuy-receipt.jpg
```

**Result:**
- Logged to "One-Time Purchases" tab
- Item: Dell 27" Monitor
- Vendor: Best Buy
- Amount: $599.99
- Purchase Date: 03/16/2026
- Notes: "Parsed from invoice: bestbuy-receipt.jpg"

### Example 3: Annual Subscription

**Your invoice shows:**
```
GitHub
Annual Subscription
Total: $48.00
Period: March 2026 - March 2027
```

**Command:**
```bash
/add-expense ~/Documents/github-annual.pdf
```

**Result:**
- Logged to "Subscriptions" tab
- Vendor: GitHub
- Monthly Cost: $4.00 (auto-calculated: $48 ÷ 12)
- Billing Cycle: Annual
- Start Date: 03/01/2026
- Contract End: 03/01/2027

## Tips & Tricks

### ✅ Best Practices

1. **Use descriptive filenames:**
   - Good: `notion-invoice-march-2026.pdf`
   - Bad: `invoice.pdf`

2. **Keep invoices organized:**
   ```
   ~/Documents/
     invoices/
       2026/
         march/
           notion-invoice.pdf
           aws-invoice.pdf
   ```

3. **For multi-page PDFs:**
   - Most invoices are 1-2 pages (works perfectly)
   - If PDF is >10 pages, skill will ask for specific pages

4. **For receipt photos:**
   - Make sure text is clear and readable
   - Good lighting helps
   - Straight angle (not tilted)

### 🔍 Troubleshooting

**Problem:** File not found error

**Solution:** Check the path
```bash
# Use absolute path
/add-expense /Users/cole/Downloads/invoice.pdf

# Or use ~ for home directory
/add-expense ~/Downloads/invoice.pdf

# Check file exists first
ls ~/Downloads/invoice.pdf
```

---

**Problem:** PDF is too large (>10 pages)

**Solution:** Use text input instead, or specify key pages
```bash
# Fallback to text
/add-expense "Notion Plus $10/mo started March 1st"
```

---

**Problem:** Data extracted incorrectly

**Solution:**
1. Check if invoice is clear and readable
2. Use text input as override
3. Or ask the skill to re-parse specific fields

## Combining Text and Files

You can still use text input whenever you prefer:

```bash
# Quick text entry
/add-expense "AWS $50/mo"

# Detailed with file
/add-expense ~/invoices/aws-detailed.pdf

# Multiple expenses (text)
/add-expense "Slack $8/mo, keyboard $89"
```

Choose whichever is faster for your workflow!

## Privacy Note

- Files are read locally on your machine
- Content is processed by Claude to extract expense data
- Extracted data is logged to your Google Sheet
- Original files are never modified or uploaded elsewhere

## What's Different from Text Input?

| Feature | Text Input | File Input |
|---------|-----------|------------|
| Speed | Fast (type & go) | Slightly slower (file read) |
| Accuracy | Depends on typing | High (reads exact amounts) |
| Convenience | Good for simple expenses | Great for detailed invoices |
| Record Keeping | Manual notes | Auto-adds filename to notes |
| Multiple Expenses | Easy with lists | One file = one expense* |

*For invoices with multiple line items, the skill may ask which to log or create multiple entries.

## Next Steps

1. **Try it now!** Find a recent invoice or receipt
2. **Save it** to your Downloads folder
3. **Run** `/add-expense ~/Downloads/your-invoice.pdf`
4. **Check** your Google Sheet to see it logged
5. **Celebrate** never manually typing invoice details again! 🎉

## Need Help?

- Text input not working? → It still works exactly the same as before
- File input issues? → Check file path and format
- Want to see what was parsed? → Check the "Notes" column in Google Sheets

## Summary

**Before:**
```bash
/add-expense "Notion Plus $10/mo started today"  # Type everything manually
```

**Now:**
```bash
/add-expense ~/Downloads/notion-invoice.pdf      # Let AI read it for you!
```

Same command, more powerful! 🚀
