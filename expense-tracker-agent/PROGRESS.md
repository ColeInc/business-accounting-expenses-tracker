# Expense Tracker Agent — Audit Progress

**Goal:** Clean up the expense spreadsheet so it accurately reflects active vs inactive
subscriptions, has no duplicates, and every service is correctly categorised as
subscription or one-time purchase.

**Last updated:** 2026-07-28

---

## 🔴 BLOCKER: Google Drive MCP not authorized

The claude.ai Google Drive MCP connector token is expired.  
Until this is re-authorized, we cannot read the live spreadsheet to:
- Build the service registry
- See what rows already exist
- Detect duplicates automatically

**Action needed from Cole:**
> Re-authorize the Google Drive MCP via claude.ai connector settings,
> then run:
> ```bash
> cd /Users/cole/Cole/PROJECTS/cole-os/02_tools/business-accounting-expense-tracker
> venv/bin/python expense-tracker-agent/context_manager.py --refresh --summary
> ```
> Paste the output back into the chat.

---

## ✅ Confirmed answers (from conversation 2026-07-28)

| Service | Status | Notes |
|---------|--------|-------|
| Apollo | Active | $59/mo — 2,500 leads/month tier |
| Instantly | Active | $47/mo — email outreach |
| Hostinger | Active | $6.99/mo |
| Airtable | Active | $24/mo |
| OpenAI | Active (ad hoc) | NOT a fixed subscription — Cole tops up credits manually when they run out. Log as **one-time purchases** each time, NOT a subscription row. |
| Apify | **Inactive** | Cole is NOT currently paying. $39/mo plan exists but is paused/cancelled. Mark as inactive in sheet if it appears. |

---

## 🟡 OPEN QUESTIONS — Need Cole's input

### 1. Zapmail — structure unclear
**What we know:**
- $194.85 one-time payment for 15 domains (8 Gmail, 7 Outlook) at $12.99/domain
- $113/mo for 30 inboxes ($3.77/inbox)
- Cole mentioned "10 new domains" — may have since expanded

**Questions for Cole:**
- [ ] Is the $194.85 a *yearly* recurring fee or a true one-time setup cost?
- [ ] Are the "10 new domains" Zapmail domains? If so, what did they cost?
- [ ] Are we currently on the 30-inbox plan ($113/mo) or have we upgraded to 50 inboxes ($188.33/mo)?
- [ ] How many separate Zapmail rows are in the spreadsheet right now?

### 2. NeverBounce — exact amount unknown
**What we know:** Approximately $30–40/mo

**Question for Cole:**
- [ ] What is the exact amount showing on your card/statement for NeverBounce?
- [ ] Is it a fixed plan or usage-based (credits)?

### 3. The "10 new domains" — source unknown
**What we know:** Cole mentioned 10 new domains were purchased recently

**Questions for Cole:**
- [ ] Are these Zapmail domains, or a different registrar (e.g. Hostinger, Namecheap, GoDaddy)?
- [ ] Have these been logged in the spreadsheet at all yet?
- [ ] What did they cost in total?

---

## 🟡 OPEN QUESTION — Full subscription list review

**We cannot do this until Google Drive MCP is re-authorized** (so we can read the actual sheet rows).

Once the sheet is readable, paste the registry summary output here and Cole will go through each row to confirm active/cancelled.

**Preliminary expected active list** (based on known Overleaf stack):
- [ ] Apollo — $59/mo — ACTIVE (confirmed)
- [ ] Instantly — $47/mo — status?
- [ ] Hostinger — $6.99/mo — status?
- [ ] Airtable — $24/mo — status?
- [ ] Zapmail (inbox plan) — $113–188/mo — status?
- [ ] NeverBounce — ~$35/mo — status?
- [ ] Apify — **INACTIVE** (confirmed, not currently paying)
- [ ] OpenAI — **NOT a subscription** (confirmed, ad hoc top-ups only)

**Any other rows in the sheet not on this list → flag as unknown, need Cole to confirm.**

---

## 📋 Action checklist

- [ ] Re-authorize Google Drive MCP connector
- [ ] Run `context_manager.py --refresh --summary` and paste output
- [ ] Confirm Zapmail structure (one-time vs recurring, current plan size)
- [ ] Confirm NeverBounce exact amount
- [ ] Confirm 10 new domains — what/where/logged?
- [ ] Review full row list from sheet → mark each active/inactive
- [ ] Remove or mark-inactive any cancelled subscriptions in the sheet
- [ ] Move OpenAI rows from Subscriptions tab to One-Time Purchases (if misclassified)
- [ ] Mark Apify as inactive in sheet (if it has a row)
- [ ] Ensure all Zapmail domain setup fees are in One-Time Purchases tab

---

## 🗺️ Architecture notes (for reference)

```
New flow:
  /expense-agent add "..." 
    → context_manager loads registry (or syncs from sheet if stale)
    → duplicate check against registry
    → if duplicate: prompt user → skip / add-anyway / update
    → if new: append to sheet + update registry

Old (blind) flow — still works but AVOID for subscriptions:
  /add-expense "..."
    → parse → blindly append (no duplicate check)
```

Registry lives at:
`expense-tracker-agent/service_registry.json` (gitignored — contains live data)
