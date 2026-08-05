#!/usr/bin/env python3
"""
Context Manager — reads the Google Sheet and maintains a local service registry.

The registry is the agent's "memory": it knows what's active, what's a duplicate,
and when things renew. It gets rebuilt on demand (or when stale > 6h).
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from typing import Optional

# Add parent dir to path so we can import sheets/config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets import SheetsClient
from config import config

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "service_registry.json")
STALE_HOURS = 6


def normalize_vendor(name: str) -> str:
    """Canonical vendor key: lowercase, no punctuation, collapsed spaces."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _parse_cost(val) -> float:
    if not val:
        return 0.0
    try:
        return float(str(val).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0


def _build_registry_from_sheet(sheets: SheetsClient) -> dict:
    """
    Read both tabs from the sheet and build a normalized registry.

    Registry shape:
    {
      "last_synced": "<iso>",
      "subscriptions": {
        "<vendor_key>": {
          "vendor": "<display name>",
          "category": "...",
          "plan_tier": "...",
          "billing_cycle": "Monthly|Annual|Quarterly",
          "monthly_cost": 59.0,
          "currency": "USD",
          "start_date": "...",
          "next_renewal": "...",
          "days_until_renewal": <int|null>,
          "auto_renew": "Yes|No",
          "payment_method": "...",
          "account_email": "...",
          "contract_end": "...",
          "notes": "...",
          "sheet_row": <int>,        # 1-based row in Subscriptions tab (incl header)
          "duplicates": [<row>,...], # rows that look like duplicates of this entry
          "status": "active|inactive|unknown",
        }
      },
      "one_time": [
        {
          "item": "...",
          "category": "...",
          "vendor": "...",
          "vendor_key": "...",
          "purchase_date": "...",
          "amount": 0.0,
          "sheet_row": <int>,
        }
      ],
      "duplicate_groups": [
        {"vendor_key": "...", "rows": [<int>,...], "display_name": "..."}
      ]
    }
    """
    registry = {
        "last_synced": datetime.utcnow().isoformat(),
        "subscriptions": {},
        "one_time": [],
        "duplicate_groups": [],
    }

    # ── Subscriptions tab ─────────────────────────────────────────────────────
    sub_rows = sheets.get_subscriptions()
    # First row is the header
    vendor_row_map: dict[str, list[int]] = {}  # vendor_key → [row indices]

    for row_idx, row in enumerate(sub_rows):
        if row_idx == 0:
            continue  # skip header
        if not row or not row[0]:
            continue

        sheet_row = row_idx + 1  # 1-based

        def _get(i, default=""):
            return row[i] if len(row) > i else default

        vendor_display = _get(0)
        vendor_key = normalize_vendor(vendor_display)

        if not vendor_key:
            continue

        # Parse days_until_renewal from column J (index 9)
        days_raw = _get(9)
        days_until = None
        try:
            if days_raw and not str(days_raw).startswith("#"):
                days_until = int(float(str(days_raw)))
        except (ValueError, TypeError):
            pass

        # Infer status from contract_end and days_until
        status = "active"
        contract_end = _get(13)
        if contract_end:
            try:
                end_dt = datetime.strptime(contract_end, "%m/%d/%Y")
                if end_dt < datetime.now():
                    status = "inactive"
            except ValueError:
                pass

        entry = {
            "vendor": vendor_display,
            "category": _get(1),
            "plan_tier": _get(2),
            "billing_cycle": _get(3),
            "monthly_cost": _parse_cost(_get(4)),
            "currency": _get(6) or "USD",
            "start_date": _get(7),
            "next_renewal": _get(8),
            "days_until_renewal": days_until,
            "auto_renew": _get(10),
            "payment_method": _get(11),
            "account_email": _get(12),
            "contract_end": contract_end,
            "notes": _get(16) if len(row) > 16 else _get(15, ""),
            "sheet_row": sheet_row,
            "status": status,
        }

        if vendor_key in vendor_row_map:
            vendor_row_map[vendor_key].append(sheet_row)
        else:
            vendor_row_map[vendor_key] = [sheet_row]

        # Keep the first occurrence as the canonical entry; track extras
        if vendor_key not in registry["subscriptions"]:
            registry["subscriptions"][vendor_key] = entry
        # (duplicates resolved below)

    # Mark duplicate rows
    for vendor_key, rows in vendor_row_map.items():
        if len(rows) > 1:
            registry["duplicate_groups"].append({
                "vendor_key": vendor_key,
                "display_name": registry["subscriptions"][vendor_key]["vendor"],
                "rows": rows,
            })

    # ── One-Time Purchases tab ────────────────────────────────────────────────
    ot_rows = sheets.get_one_time_purchases()
    for row_idx, row in enumerate(ot_rows):
        if row_idx == 0:
            continue
        if not row or not row[0]:
            continue

        def _get(i, default=""):
            return row[i] if len(row) > i else default

        registry["one_time"].append({
            "item": _get(0),
            "category": _get(1),
            "vendor": _get(2),
            "vendor_key": normalize_vendor(_get(2)),
            "purchase_date": _get(3),
            "amount": _parse_cost(_get(4)),
            "sheet_row": row_idx + 1,
        })

    return registry


def load_registry(force_refresh: bool = False) -> dict:
    """Return the registry, refreshing from the sheet if stale or missing."""
    if not force_refresh and os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH) as f:
            reg = json.load(f)
        synced = datetime.fromisoformat(reg.get("last_synced", "2000-01-01"))
        if datetime.utcnow() - synced < timedelta(hours=STALE_HOURS):
            return reg

    print("Syncing service registry from Google Sheets...", file=sys.stderr)
    sheets = SheetsClient()
    registry = _build_registry_from_sheet(sheets)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)
    print(f"Registry saved to {REGISTRY_PATH}", file=sys.stderr)
    return registry


def find_duplicate(vendor: str, registry: dict) -> Optional[dict]:
    """Return the existing registry entry if this vendor is already tracked."""
    key = normalize_vendor(vendor)
    return registry["subscriptions"].get(key)


def get_upcoming_renewals(registry: dict, days: int = 14) -> list:
    """Return subscriptions renewing within `days` days, sorted by urgency."""
    upcoming = []
    for entry in registry["subscriptions"].values():
        d = entry.get("days_until_renewal")
        if d is not None and 0 <= d <= days:
            upcoming.append(entry)
    return sorted(upcoming, key=lambda x: x["days_until_renewal"])


def print_registry_summary(registry: dict):
    """Human-readable state-of-subscriptions report."""
    subs = registry["subscriptions"]
    dups = registry["duplicate_groups"]
    ot = registry["one_time"]

    active = [s for s in subs.values() if s["status"] == "active"]
    inactive = [s for s in subs.values() if s["status"] == "inactive"]
    unknown = [s for s in subs.values() if s["status"] == "unknown"]

    total_monthly = sum(s["monthly_cost"] for s in active)

    print(f"\n{'='*60}")
    print(f"SERVICE REGISTRY SUMMARY  (synced {registry['last_synced'][:16]} UTC)")
    print(f"{'='*60}")
    print(f"\n ACTIVE SUBSCRIPTIONS ({len(active)})  —  ${total_monthly:.2f}/mo total")
    print(f" {'─'*56}")
    for s in sorted(active, key=lambda x: x["monthly_cost"], reverse=True):
        renewal = f"  renews in {s['days_until_renewal']}d" if s["days_until_renewal"] is not None else ""
        print(f"  {s['vendor']:<25} ${s['monthly_cost']:>8.2f}/mo  {s['billing_cycle']:<10}{renewal}")

    if inactive:
        print(f"\n INACTIVE / CANCELLED ({len(inactive)})")
        print(f" {'─'*56}")
        for s in inactive:
            print(f"  {s['vendor']:<25}  ended {s['contract_end']}")

    if dups:
        print(f"\n DUPLICATE ENTRIES DETECTED ({len(dups)} vendor(s))")
        print(f" {'─'*56}")
        for d in dups:
            print(f"  {d['display_name']}  →  rows {d['rows']}")

    renewals = get_upcoming_renewals(registry, days=14)
    if renewals:
        print(f"\n UPCOMING RENEWALS (next 14 days)")
        print(f" {'─'*56}")
        for r in renewals:
            print(f"  {r['vendor']:<25} in {r['days_until_renewal']}d  (${r['monthly_cost']:.2f}/mo)")

    print(f"\n ONE-TIME PURCHASES: {len(ot)} total")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Expense tracker context manager")
    parser.add_argument("--refresh", action="store_true", help="Force refresh from sheet")
    parser.add_argument("--summary", action="store_true", help="Print registry summary")
    args = parser.parse_args()

    reg = load_registry(force_refresh=args.refresh)
    if args.summary:
        print_registry_summary(reg)
    else:
        print(json.dumps(reg, indent=2))
