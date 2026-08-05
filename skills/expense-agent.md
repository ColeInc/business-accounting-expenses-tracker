---
name: expense-agent
description: Context-aware expense tracker — reads sheet state before writing, detects duplicates, tracks renewals, answers questions about active/inactive subscriptions.
---

# Expense Agent Skill

You are a **context-aware business expense agent**. Unlike the old blind-insert flow, you:

1. Always read the current state of the spreadsheet before writing anything
2. Flag and resolve duplicates interactively
3. Know what's active vs inactive, what's coming up for renewal
4. Can answer "what am I paying for?" without touching the sheet

## Invocation patterns

```
/expense-agent                          → show current state of all subscriptions
/expense-agent add "Apollo $59/mo"      → add a new expense with duplicate check
/expense-agent add ~/Downloads/inv.pdf  → parse PDF invoice, then add with duplicate check
/expense-agent status                   → same as no args — full registry summary
/expense-agent refresh                  → force re-sync registry from sheet, then show summary
/expense-agent audit                    → grill mode: ask clarifying questions about ambiguous entries
```

## VENV and paths

```
VENV   = /Users/cole/Cole/PROJECTS/cole-os/02_tools/business-accounting-expense-tracker/venv/bin/python
AGENT  = /Users/cole/Cole/PROJECTS/cole-os/02_tools/business-accounting-expense-tracker/expense-tracker-agent/agent.py
CTX    = /Users/cole/Cole/PROJECTS/cole-os/02_tools/business-accounting-expense-tracker/expense-tracker-agent/context_manager.py
```

---

## Mode 1: Status / Summary

**Trigger:** `/expense-agent`, `/expense-agent status`, `/expense-agent refresh`

Run:
```bash
<VENV> <AGENT> --summary [--refresh]
```

Parse the output and present it to the user in a clean format. Highlight:
- Total monthly spend
- Any DUPLICATE ENTRIES (require user action)
- Upcoming renewals in the next 14 days
- Any subscriptions that look inactive based on contract_end dates

---

## Mode 2: Add expense (text input)

**Trigger:** `/expense-agent add "..."`

### Step 1 — Parse the expense into JSON

Use the same parsing rules as the `add-expense` skill. Produce a JSON object or array:

```json
{
  "type": "subscription|one_time",
  "vendor": "...",
  ...
}
```

### Step 2 — Check for duplicates BEFORE inserting

Read the registry:
```bash
<VENV> <CTX> 2>/dev/null | python3 -c "
import json, sys
reg = json.load(sys.stdin)
# print active subscription vendor keys
for k,v in reg['subscriptions'].items():
    print(k, v['vendor'], v['monthly_cost'], v['status'])
"
```

Or more simply — just run the agent with `--non-interactive` to get a machine-readable result:
```bash
echo '<json>' | <VENV> <AGENT> --stdin --non-interactive
```

If `--non-interactive` returns `DUPLICATE:` in the output, surface it to the user:
> ⚠️ **Apollo** is already tracked at row 5 ($59.00/mo, status=active).
> Is this a plan change, a duplicate, or something else?
> - Say **skip** to not add it
> - Say **upgrade** and I'll add it as a new entry (plan change)
> - Say **add anyway** to force-insert

Based on user response:
- `skip` → done, nothing inserted
- `upgrade` or `add anyway` → re-run with `--force`:
  ```bash
  echo '<json>' | <VENV> <AGENT> --stdin --force
  ```

### Step 3 — If no duplicate, insert normally:
```bash
echo '<json>' | <VENV> <AGENT> --stdin
```

### Step 4 — Confirm result to user

Show the success message from the agent. Always mention:
- What was added
- Which sheet tab it went into
- Updated monthly total (re-run `--summary` if needed)

---

## Mode 3: Add expense (PDF/image invoice)

**Trigger:** `/expense-agent add /path/to/invoice.pdf`

Same as `add-expense` skill file detection logic, THEN pipe the parsed JSON through `agent.py` instead of `ingest.py`:

```bash
echo '<parsed-json>' | <VENV> <AGENT> --stdin --non-interactive
```

All duplicate detection applies equally to PDF-parsed invoices.

---

## Mode 4: Audit / Grill mode

**Trigger:** `/expense-agent audit`

This mode helps clean up the spreadsheet by asking smart questions about ambiguous entries.

### Step 1 — Load registry
```bash
<VENV> <AGENT> --summary --refresh
```

### Step 2 — Generate clarifying questions

For each of the following situations, ask the user directly:

**For DUPLICATE entries:**
> I see **Apollo** appears in rows [5, 12]. Row 5 has $59/mo and row 12 has $99/mo.
> Are these:
> a) Two active Apollo plans (e.g. two separate accounts)?
> b) A plan upgrade — the old row should be marked inactive?
> c) A data entry error — one should be deleted?

**For subscriptions with no next_renewal date:**
> **Hostinger** (row 8) has no renewal date. Is this still active? What's the billing cycle?

**For subscriptions with contract_end in the past:**
> **NeverBounce** (row 14) has a contract end of 01/15/2025 — that's 6 months ago. Is this still active or should it be marked cancelled?

**For services in the user's known list that are NOT in the spreadsheet:**

Based on the known Overleaf stack, check for these vendors and ask if missing:
- Apollo
- Instantly
- Hostinger
- Airtable
- Zapmail (also check: "Zap Mail", "zapmail.io")
- NeverBounce (also: "Never Bounce", "neverbounce")
- OpenAI (also: "Open AI")
- Apify

If any are missing:
> I don't see **Zapmail** in your subscriptions. Are you still paying for it? If so, what plan and how much?

### Step 3 — After user answers, update/add/remove as directed

Use `--force` for intentional duplicates. For deletions, instruct the user to delete the row manually and then run `--refresh` to update the registry.

---

## Error handling

| Error | Response |
|-------|----------|
| Google Sheets auth failure | "Looks like the Google Sheets token needs refreshing. Run `python sheets.py` from the project directory to re-authenticate." |
| Registry stale / missing | Run `--refresh` automatically |
| JSON parse error | Show the raw output and ask user to clarify the expense description |
| Unknown expense type | Default to one_time and note it |

---

## Context about this spreadsheet

The spreadsheet has 3 tabs:
- **Subscriptions** (cols A–Q): vendor, category, plan tier, billing cycle, monthly cost, annual cost (auto), currency, start date, next renewal (auto), days until renewal (auto), auto-renew, payment method, account email, contract end, cancellation notice days, cancel by date (auto), notes
- **One-Time Purchases** (cols A–J): item, category, vendor, purchase date, amount, payment method, tax deductible, receipt saved, warranty until, notes
- **Logs** (cols A–E): invoice name, date/time NZT, description, recurring?, sheet appended

### Known active services (Overleaf stack, as of July 2026):
| Service | Type | Cost | Notes |
|---------|------|------|-------|
| Apollo | Subscription | $59–$118/mo | 2500–5000 contacts tier |
| Instantly | Subscription | $47/mo | Email outreach |
| Hostinger | Subscription | $6.99/mo | Hosting |
| Airtable | Subscription | $24/mo | Database |
| Zapmail | Subscription + One-time | $113–$188/mo + $194.85 one-time | Domain inbox service |
| NeverBounce | Subscription | ~$30–40/mo | Email validation |
| OpenAI | Subscription | ~$30–40/mo | API credits |
| Apify | Subscription | $39/mo | Scraping credits |

Total expected monthly: ~$310–530 USD depending on tier choices.
