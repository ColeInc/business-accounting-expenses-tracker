#!/usr/bin/env python3
"""
Expense Tracker Agent — context-aware ingestion with duplicate detection.

Unlike the blind ingest.py, this agent:
  1. Reads the full sheet state into a local registry before writing anything
  2. Checks every new expense against known vendors
  3. Flags duplicates and asks for confirmation before inserting
  4. Updates the registry after a successful write
  5. Can generate a full "state of my subscriptions" report on demand
"""

import json
import os
import sys
from typing import Any

# Add parent dir so we can import existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context_manager import (
    load_registry,
    find_duplicate,
    normalize_vendor,
    print_registry_summary,
    REGISTRY_PATH,
)
from sheets import SheetsClient
from models import Subscription, OneTimePurchase
from validator import validate_subscription, validate_one_time
from utils import format_expense_summary


# ── Duplicate resolution options ──────────────────────────────────────────────

def _prompt_duplicate_resolution(vendor: str, existing: dict, new_expense: dict) -> str:
    """
    Print a summary of the conflict and return the user's chosen action.
    Returns: "skip" | "add" | "update"
    """
    print(f"\n⚠️  DUPLICATE DETECTED: {vendor}")
    print(f"   Existing entry (row {existing['sheet_row']}):")
    print(f"     Plan:    {existing.get('plan_tier', 'N/A')}  |  ${existing.get('monthly_cost', 0):.2f}/mo  |  {existing.get('billing_cycle', 'N/A')}")
    print(f"     Status:  {existing.get('status', 'unknown')}")
    print(f"     Started: {existing.get('start_date', 'N/A')}")
    print(f"\n   New expense being added:")
    if new_expense.get("type") == "subscription":
        print(f"     Plan:    {new_expense.get('plan_tier', 'N/A')}  |  ${new_expense.get('monthly_cost', 0):.2f}/mo  |  {new_expense.get('billing_cycle', 'N/A')}")
    else:
        print(f"     Amount:  ${new_expense.get('amount', 0):.2f}  on  {new_expense.get('purchase_date', 'N/A')}")

    print("\n   Options:")
    print("     [s] Skip — don't add this (it's already tracked)")
    print("     [a] Add anyway — add as a new row (intentional duplicate, e.g. plan upgrade)")
    print("     [u] Update — not implemented in CLI; edit the sheet directly")
    print()

    while True:
        choice = input("   Your choice [s/a/u]: ").strip().lower()
        if choice in ("s", "a", "u"):
            return {"s": "skip", "a": "add", "u": "update"}[choice]
        print("   Please enter s, a, or u")


# ── Core agent logic ──────────────────────────────────────────────────────────

def process_expense_with_context(
    expense: dict[str, Any],
    registry: dict,
    sheets: SheetsClient,
    non_interactive: bool = False,
    force_add: bool = False,
) -> dict[str, Any]:
    """
    Process a single expense with full duplicate awareness.

    Returns:
      {
        "action": "added" | "skipped" | "duplicate_flagged",
        "vendor": "...",
        "message": "...",
        "expense": {...},
      }
    """
    expense_type = expense.get("type", "unknown")
    vendor = expense.get("vendor", "") or expense.get("item", "Unknown")

    # ── Duplicate check (subscriptions only — one-time purchases are always unique) ──
    if expense_type == "subscription":
        existing = find_duplicate(vendor, registry)
        if existing and not force_add:
            if non_interactive:
                return {
                    "action": "duplicate_flagged",
                    "vendor": vendor,
                    "existing_row": existing["sheet_row"],
                    "message": (
                        f"DUPLICATE: {vendor} already tracked at row {existing['sheet_row']} "
                        f"(${existing['monthly_cost']:.2f}/mo, status={existing['status']}). "
                        f"Use --force to add anyway."
                    ),
                    "expense": expense,
                }
            else:
                action = _prompt_duplicate_resolution(vendor, existing, expense)
                if action == "skip":
                    return {
                        "action": "skipped",
                        "vendor": vendor,
                        "message": f"Skipped {vendor} — already tracked at row {existing['sheet_row']}.",
                        "expense": expense,
                    }
                elif action == "update":
                    return {
                        "action": "skipped",
                        "vendor": vendor,
                        "message": f"Update not implemented in CLI. Edit row {existing['sheet_row']} in the sheet directly.",
                        "expense": expense,
                    }
                # action == "add": fall through to insert

    # ── Insert into sheet ─────────────────────────────────────────────────────
    try:
        if expense_type == "subscription":
            validated = validate_subscription(expense)
            model_data = {k: v for k, v in validated.items() if k != "type"}
            sub = Subscription(**model_data)
            sheets.append_subscription(sub)
            summary = format_expense_summary(validated)
            message = f"✅ Added to Subscriptions:\n{summary}"

            # Update registry in memory
            key = normalize_vendor(vendor)
            registry["subscriptions"][key] = {
                "vendor": vendor,
                "category": validated.get("category", ""),
                "plan_tier": validated.get("plan_tier", ""),
                "billing_cycle": validated.get("billing_cycle", "Monthly"),
                "monthly_cost": validated.get("monthly_cost", 0),
                "currency": validated.get("currency", "USD"),
                "start_date": validated.get("start_date", ""),
                "next_renewal": "",
                "days_until_renewal": None,
                "auto_renew": validated.get("auto_renew", "Yes"),
                "payment_method": validated.get("payment_method", ""),
                "account_email": validated.get("account_email", ""),
                "contract_end": validated.get("contract_end", ""),
                "notes": validated.get("notes", ""),
                "sheet_row": -1,  # unknown until we refresh
                "status": "active",
            }

        elif expense_type == "one_time":
            validated = validate_one_time(expense)
            model_data = {k: v for k, v in validated.items() if k != "type"}
            purchase = OneTimePurchase(**model_data)
            sheets.append_one_time(purchase)
            summary = format_expense_summary(validated)
            message = f"✅ Added to One-Time Purchases:\n{summary}"

            registry["one_time"].append({
                "item": validated.get("item", ""),
                "category": validated.get("category", ""),
                "vendor": vendor,
                "vendor_key": normalize_vendor(vendor),
                "purchase_date": validated.get("purchase_date", ""),
                "amount": validated.get("amount", 0),
                "sheet_row": -1,
            })

        else:
            return {
                "action": "error",
                "vendor": vendor,
                "message": f"❌ Unknown expense type: {expense_type}",
                "expense": expense,
            }

        # Persist updated registry
        import json as _json
        with open(REGISTRY_PATH, "w") as f:
            _json.dump(registry, f, indent=2)

        return {"action": "added", "vendor": vendor, "message": message, "expense": expense}

    except Exception as e:
        return {
            "action": "error",
            "vendor": vendor,
            "message": f"❌ Error inserting {vendor}: {e}",
            "expense": expense,
        }


def run_agent(
    expenses: list[dict],
    non_interactive: bool = False,
    force_add: bool = False,
    refresh_registry: bool = False,
) -> list[dict]:
    """Process a list of expenses with full context awareness."""
    registry = load_registry(force_refresh=refresh_registry)
    sheets = SheetsClient()
    results = []

    for expense in expenses:
        result = process_expense_with_context(
            expense, registry, sheets,
            non_interactive=non_interactive,
            force_add=force_add,
        )
        results.append(result)
        print(result["message"])

    return results


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Context-aware expense tracker agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a single expense (JSON string)
  echo '{"type":"subscription","vendor":"Apollo","monthly_cost":59}' | python agent.py --stdin

  # Add from JSON array
  echo '[{...},{...}]' | python agent.py --stdin

  # Show registry summary (current state of all subscriptions)
  python agent.py --summary

  # Force refresh registry from sheet, then show summary
  python agent.py --summary --refresh

  # Non-interactive mode (for automation — flags duplicates instead of prompting)
  echo '{...}' | python agent.py --stdin --non-interactive

  # Force-add even if duplicate (e.g. intentional plan upgrade)
  echo '{...}' | python agent.py --stdin --force
        """,
    )
    parser.add_argument("--stdin", action="store_true", help="Read expense JSON from stdin")
    parser.add_argument("--summary", action="store_true", help="Print registry summary and exit")
    parser.add_argument("--refresh", action="store_true", help="Force refresh registry from sheet")
    parser.add_argument("--non-interactive", action="store_true", dest="non_interactive",
                        help="Flag duplicates instead of prompting (for automation)")
    parser.add_argument("--force", action="store_true", help="Add even if duplicate exists")
    parser.add_argument("json_arg", nargs="?", help="JSON string (alternative to --stdin)")

    args = parser.parse_args()

    if args.summary:
        registry = load_registry(force_refresh=args.refresh)
        print_registry_summary(registry)
        return

    # Read JSON
    json_data = None
    if args.stdin:
        json_data = sys.stdin.read().strip()
    elif args.json_arg:
        json_data = args.json_arg

    if not json_data:
        parser.print_help()
        sys.exit(1)

    try:
        parsed = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)

    expenses = [parsed] if isinstance(parsed, dict) else parsed

    results = run_agent(
        expenses,
        non_interactive=args.non_interactive,
        force_add=args.force,
        refresh_registry=args.refresh,
    )

    # Exit with error code if any expense had an error (useful for CI/automation)
    if any(r["action"] == "error" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
