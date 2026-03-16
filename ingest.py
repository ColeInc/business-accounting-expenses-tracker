#!/usr/bin/env python3
"""
Expense Ingestion Script
Accepts pre-parsed JSON from Claude and inserts to Google Sheets
"""

import sys
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any
from validator import validate_subscription, validate_one_time
from sheets import SheetsClient
from models import Subscription, OneTimePurchase
from utils import format_expense_summary
from config import config


def get_nzt_datetime() -> str:
    """Get current datetime in NZT format"""
    nzt = ZoneInfo('Pacific/Auckland')
    return datetime.now(nzt).strftime('%Y-%m-%d %H:%M:%S NZT')


def log_locally(log_entry: Dict[str, Any]) -> None:
    """Append a log entry to the local JSON log file"""
    log_path = config.LOCAL_LOG_PATH

    # Load existing logs or create new list
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)

    with open(log_path, 'w') as f:
        json.dump(logs, f, indent=2)


def process_expenses(expenses: List[Dict[str, Any]], invoice_name: str = None) -> str:
    """
    Process list of parsed expenses
    Returns formatted summary message
    """
    results = []

    try:
        if not expenses:
            return "❌ No expenses found in input"

        # Initialize sheets client
        sheets = SheetsClient()

        # Ensure Logs sheet exists if logging is enabled
        if invoice_name:
            sheets.ensure_logs_sheet_exists()

        # Process each expense
        for expense in expenses:
            expense_type = expense.get('type', 'unknown')
            sheet_appended = None
            is_recurring = False
            description = ""

            if expense_type == 'subscription':
                # Validate and insert subscription
                validated = validate_subscription(expense)
                # Remove 'type' field before passing to model
                model_data = {k: v for k, v in validated.items() if k != 'type'}
                sub = Subscription(**model_data)
                sheets.append_subscription(sub)

                summary = format_expense_summary(validated)
                results.append(f"✅ Logged to Subscriptions:\n{summary}")

                sheet_appended = config.SUBSCRIPTIONS_TAB
                is_recurring = True
                description = f"{validated.get('vendor', 'Unknown')} - {validated.get('plan_tier', '')} ({validated.get('billing_cycle', 'Monthly')}) - ${validated.get('monthly_cost', 0)}/mo"

            elif expense_type == 'one_time':
                # Validate and insert one-time purchase
                validated = validate_one_time(expense)
                # Remove 'type' field before passing to model
                model_data = {k: v for k, v in validated.items() if k != 'type'}
                purchase = OneTimePurchase(**model_data)
                sheets.append_one_time(purchase)

                summary = format_expense_summary(validated)
                results.append(f"✅ Logged to One-Time Purchases:\n{summary}")

                sheet_appended = config.ONE_TIME_TAB
                is_recurring = False
                description = f"{validated.get('item', 'Unknown')} from {validated.get('vendor', 'Unknown')} - ${validated.get('amount', 0)}"

            else:
                results.append(f"❌ Unknown expense type: {expense_type}")
                continue

            # Log to both local file and Google Sheets Logs tab
            if invoice_name and sheet_appended:
                datetime_nzt = get_nzt_datetime()

                # Local log entry
                log_entry = {
                    "invoice_name": invoice_name,
                    "datetime_nzt": datetime_nzt,
                    "description": description,
                    "is_recurring": is_recurring,
                    "sheet_appended": sheet_appended,
                    "expense_data": expense
                }
                log_locally(log_entry)

                # Google Sheets log entry
                sheets.append_log(
                    invoice_name=invoice_name,
                    datetime_nzt=datetime_nzt,
                    description=description,
                    is_recurring=is_recurring,
                    sheet_appended=sheet_appended
                )

        return "\n\n".join(results) + "\n\nRow(s) appended to your Google Sheet."

    except Exception as e:
        return f"❌ Error processing expense: {str(e)}"


def main():
    """Main entry point"""
    try:
        # Parse arguments
        invoice_name = None
        args = sys.argv[1:]

        # Extract --invoice-name if present
        if '--invoice-name' in args:
            idx = args.index('--invoice-name')
            if idx + 1 < len(args):
                invoice_name = args[idx + 1]
                args = args[:idx] + args[idx + 2:]

        # Read JSON from stdin or command-line arg
        if '--stdin' in args:
            json_data = sys.stdin.read()
        elif len(args) >= 1 and args[0] != '--stdin':
            # For testing: python ingest.py '{"type":"subscription",...}'
            json_data = args[0]
        else:
            print("Usage:")
            print("  echo '<json>' | python ingest.py --stdin [--invoice-name <name>]")
            print("  python ingest.py '<json>' [--invoice-name <name>]")
            print("\nExamples:")
            print('  echo \'{"type":"subscription","vendor":"Notion",...}\' | python ingest.py --stdin')
            print('  python ingest.py \'[{"type":"one_time","item":"Monitor",...}]\' --invoice-name "receipt.pdf"')
            sys.exit(1)

        # Parse JSON
        parsed = json.loads(json_data)

        # Ensure we have a list
        if isinstance(parsed, dict):
            expenses = [parsed]
        elif isinstance(parsed, list):
            expenses = parsed
        else:
            print("❌ Invalid JSON format. Expected object or array.")
            sys.exit(1)

        # Process and print result
        result = process_expenses(expenses, invoice_name=invoice_name)
        print(result)

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
