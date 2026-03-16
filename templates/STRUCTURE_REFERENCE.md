# Google Sheets Structure Reference

## Visual Sheet Layout

### 📊 Subscriptions Tab (16 columns)

```
┌───────────┬──────────┬───────────┬──────────────┬──────────────┬─────────────┬────────────┬──────────────┐
│  Vendor   │ Category │ Plan Tier │ Billing Cycle│ Monthly Cost │ Annual Cost │ Start Date │ Next Renewal │
│    (A)    │   (B)    │    (C)    │     (D)      │     (E)      │ (F) CALC    │    (G)     │  (H) CALC    │
├───────────┼──────────┼───────────┼──────────────┼──────────────┼─────────────┼────────────┼──────────────┤
│  Notion   │Productivity│  Plus    │   Monthly    │     10       │    120      │ 2024-01-15 │  2024-04-15  │
│   Slack   │Communication│Business+│   Annual     │     80       │    960      │ 2023-11-01 │  2024-11-01  │
└───────────┴──────────┴───────────┴──────────────┴──────────────┴─────────────┴────────────┴──────────────┘

┌──────────────────┬────────────┬────────────────┬──────────────┬──────────────────┬────────────────┬──────────┐
│ Days Until Renewal│ Auto Renew │ Payment Method │ Account Email│  Contract End    │ Cancellation   │Cancel By │
│     (I) CALC      │    (J)     │      (K)       │     (L)      │       (M)        │  Notice Days   │  Date    │
│                   │            │                │              │                  │      (N)       │(O) CALC  │
├──────────────────┼────────────┼────────────────┼──────────────┼──────────────────┼────────────────┼──────────┤
│        30        │    Yes     │Business CC     │team@co.com   │                  │                │          │
│       214        │    Yes     │Business CC     │admin@co.com  │   2025-10-31     │      30        │2025-10-01│
└──────────────────┴────────────┴────────────────┴──────────────┴──────────────────┴────────────────┴──────────┘

┌─────────────────────────────────────────────────────────────┐
│                          Notes (P)                          │
├─────────────────────────────────────────────────────────────┤
│              Team workspace for documentation               │
│            Company-wide team communication                  │
└─────────────────────────────────────────────────────────────┘
```

**Auto-Calculated Columns:**
- **F (Annual Cost):** `=E*12`
- **H (Next Renewal):** Calculates next renewal based on billing cycle and start date
- **I (Days Until Renewal):** `=H-TODAY()`
- **O (Cancel By Date):** `=M-N` (Contract End minus Notice Days)

---

### 🛒 One-Time Purchases Tab (10 columns)

```
┌─────────────────┬────────────────┬──────────┬──────────────┬────────┬────────────────┬──────────────┬────────────┐
│      Item       │    Category    │  Vendor  │Purchase Date │ Amount │ Payment Method │Tax Deductible│Receipt Saved│
│       (A)       │      (B)       │   (C)    │     (D)      │  (E)   │      (F)       │     (G)      │    (H)     │
├─────────────────┼────────────────┼──────────┼──────────────┼────────┼────────────────┼──────────────┼────────────┤
│ Standing Desk   │   Furniture    │  IKEA    │  2024-01-20  │  599   │  Business CC   │     Yes      │    Yes     │
│Ergonomic Mouse  │   Equipment    │ Logitech │  2024-02-15  │ 89.99  │  Business CC   │     Yes      │    Yes     │
│Stock Photos     │   Branding     │  Adobe   │  2024-03-01  │  249   │  Business CC   │     Yes      │    Yes     │
└─────────────────┴────────────────┴──────────┴──────────────┴────────┴────────────────┴──────────────┴────────────┘

┌────────────────┬───────────────────────────────────────────────────┐
│ Warranty Until │                    Notes (J)                      │
│      (I)       │                                                   │
├────────────────┼───────────────────────────────────────────────────┤
│  2026-01-20    │  Adjustable height desk for home office          │
│  2025-02-15    │  MX Master 3S for developer workstation           │
│                │  10 high-res images for marketing website         │
└────────────────┴───────────────────────────────────────────────────┘
```

---

### 📝 Logs Tab (5 columns) - Auto-Created

```
┌─────────────────────────┬─────────────────────┬────────────────────────────────────────┬───────────┬─────────────────┐
│     Invoice Name        │  Date/Time (NZT)    │              Description               │Recurring? │ Sheet Appended  │
│          (A)            │        (B)          │                  (C)                   │    (D)    │      (E)        │
├─────────────────────────┼─────────────────────┼────────────────────────────────────────┼───────────┼─────────────────┤
│invoice_slack_2024.pdf   │2024-03-15 14:23:45  │Slack - Business+ (Annual) - $80/mo     │    Yes    │  Subscriptions  │
│receipt_mouse.pdf        │2024-02-15 09:15:22  │Ergonomic Mouse from Logitech - $89.99  │    No     │One-Time Purchases│
│invoice_notion_jan.pdf   │2024-01-15 16:42:11  │Notion - Plus (Monthly) - $10/mo        │    Yes    │  Subscriptions  │
└─────────────────────────┴─────────────────────┴────────────────────────────────────────┴───────────┴─────────────────┘
```

**Purpose:** Audit trail of expenses processed from PDF/image files.

---

## Column Details

### Subscriptions (A-P)

| Col | Name | Type | Required | Notes |
|-----|------|------|----------|-------|
| A | Vendor | Text | ✅ | Service provider name |
| B | Category | Text | ✅ | Must match valid categories |
| C | Plan Tier | Text | ⚪ | e.g., "Plus", "Pro", "Enterprise" |
| D | Billing Cycle | Text | ⚪ | "Monthly", "Annual", or "Quarterly" |
| E | Monthly Cost | Number | ✅ | Amount in dollars |
| F | Annual Cost | Number | 🤖 | Auto: `=E*12` |
| G | Start Date | Date | ⚪ | YYYY-MM-DD format |
| H | Next Renewal | Date | 🤖 | Auto: Based on cycle + start date |
| I | Days Until Renewal | Number | 🤖 | Auto: `=H-TODAY()` |
| J | Auto Renew | Text | ⚪ | "Yes" or "No" |
| K | Payment Method | Text | ⚪ | e.g., "Business Credit Card" |
| L | Account Email | Email | ⚪ | Login email for service |
| M | Contract End | Date | ⚪ | Contract expiration date |
| N | Cancellation Notice Days | Number | ⚪ | Days notice to cancel |
| O | Cancel By Date | Date | 🤖 | Auto: `=M-N` |
| P | Notes | Text | ⚪ | Additional information |

**Legend:** ✅ Required | ⚪ Optional | 🤖 Auto-calculated

### One-Time Purchases (A-J)

| Col | Name | Type | Required | Notes |
|-----|------|------|----------|-------|
| A | Item | Text | ✅ | What was purchased |
| B | Category | Text | ✅ | Must match valid categories |
| C | Vendor | Text | ⚪ | Where purchased from |
| D | Purchase Date | Date | ⚪ | YYYY-MM-DD format |
| E | Amount | Number | ✅ | Purchase amount in dollars |
| F | Payment Method | Text | ⚪ | How it was paid |
| G | Tax Deductible | Text | ⚪ | "Yes" or "No" |
| H | Receipt Saved | Text | ⚪ | "Yes" or "No" |
| I | Warranty Until | Date | ⚪ | Warranty expiration |
| J | Notes | Text | ⚪ | Additional information |

### Logs (A-E)

| Col | Name | Type | Auto-Populated | Notes |
|-----|------|------|----------------|-------|
| A | Invoice Name | Text | ✅ | Source filename |
| B | Date/Time (NZT) | DateTime | ✅ | Processing timestamp |
| C | Description | Text | ✅ | Expense summary |
| D | Recurring? | Text | ✅ | "Yes" or "No" |
| E | Sheet Appended | Text | ✅ | Target sheet name |

---

## Valid Category Values

### Subscriptions
```
Accounting       Analytics      Communication    CRM
Design           Development    Hosting          Legal
Marketing        Payroll        Productivity     Project Mgmt
Security         Storage        Other
```

### One-Time Purchases
```
Branding         Equipment      Furniture        Legal Fees
Licenses         Office Supplies Software License Training
Web              Other
```

---

## Formula Reference

### Subscriptions Formulas

**Annual Cost (Column F):**
```excel
=E2*12
```

**Next Renewal (Column H):**
```excel
=IF(D2="Monthly",
    DATE(YEAR(G2),MONTH(G2)+1,DAY(G2)),
    IF(D2="Annual",
        DATE(YEAR(G2)+1,MONTH(G2),DAY(G2)),
        DATE(YEAR(G2),MONTH(G2)+3,DAY(G2))
    )
)
```

**Days Until Renewal (Column I):**
```excel
=H2-TODAY()
```

**Cancel By Date (Column O):**
```excel
=IF(M2="", "", M2-N2)
```

---

## Color Coding Suggestions

Apply conditional formatting for better visibility:

### Subscriptions
- 🟠 **Orange** - Days Until Renewal < 30 (expiring soon)
- 🟡 **Yellow** - Auto Renew = "No" (manual renewal required)
- 🔴 **Red** - Days Until Renewal < 7 (urgent)

### One-Time Purchases
- 🟢 **Green** - Receipt Saved = "Yes"
- 🟡 **Yellow** - Tax Deductible = "Yes"

---

## Data Validation Recommendations

### Dropdowns

**Subscriptions → Category (B):**
```
Accounting,Analytics,Communication,CRM,Design,Development,Hosting,Legal,Marketing,Payroll,Productivity,Project Mgmt,Security,Storage,Other
```

**Subscriptions → Billing Cycle (D):**
```
Monthly,Annual,Quarterly
```

**Subscriptions → Auto Renew (J):**
```
Yes,No
```

**One-Time Purchases → Category (B):**
```
Branding,Equipment,Furniture,Legal Fees,Licenses,Office Supplies,Software License,Training,Web,Other
```

**One-Time Purchases → Tax Deductible (G):**
```
Yes,No
```

**One-Time Purchases → Receipt Saved (H):**
```
Yes,No
```

---

## Quick Import Guide

### Google Sheets
1. Create new sheet
2. File → Import → Upload
3. Import each CSV as a separate sheet
4. Rename sheets to match tab names

### Excel
1. Run `python templates/generate_excel_template.py`
2. Upload generated `.xlsx` to Google Drive
3. Right-click → Open with → Google Sheets

### Manual Setup
1. Copy column headers from TEMPLATE_README.md
2. Add formulas for auto-calculated columns
3. Set up data validation dropdowns
4. Apply conditional formatting
