#!/usr/bin/env python3
"""
Expense Ingestion Script
Accepts pre-parsed JSON from Claude and inserts to Google Sheets
"""

import sys
import json
from typing import List, Dict, Any
from validator import validate_subscription, validate_one_time
from sheets import SheetsClient
from models import Subscription, OneTimePurchase
from utils import format_expense_summary


def process_expenses(expenses: List[Dict[str, Any]]) -> str:
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

        # Process each expense
        for expense in expenses:
            expense_type = expense.get('type', 'unknown')

            if expense_type == 'subscription':
                # Validate and insert subscription
                validated = validate_subscription(expense)
                # Remove 'type' field before passing to model
                model_data = {k: v for k, v in validated.items() if k != 'type'}
                sub = Subscription(**model_data)
                sheets.append_subscription(sub)

                summary = format_expense_summary(validated)
                results.append(f"✅ Logged to Subscriptions:\n{summary}")

            elif expense_type == 'one_time':
                # Validate and insert one-time purchase
                validated = validate_one_time(expense)
                # Remove 'type' field before passing to model
                model_data = {k: v for k, v in validated.items() if k != 'type'}
                purchase = OneTimePurchase(**model_data)
                sheets.append_one_time(purchase)

                summary = format_expense_summary(validated)
                results.append(f"✅ Logged to One-Time Purchases:\n{summary}")

            else:
                results.append(f"❌ Unknown expense type: {expense_type}")

        return "\n\n".join(results) + "\n\nRow(s) appended to your Google Sheet."

    except Exception as e:
        return f"❌ Error processing expense: {str(e)}"


def main():
    """Main entry point"""
    try:
        # Read JSON from stdin or command-line arg
        if '--stdin' in sys.argv:
            json_data = sys.stdin.read()
        elif len(sys.argv) >= 2:
            # For testing: python ingest.py '{"type":"subscription",...}'
            json_data = sys.argv[1]
        else:
            print("Usage:")
            print("  echo '<json>' | python ingest.py --stdin")
            print("  python ingest.py '<json>'")
            print("\nExamples:")
            print('  echo \'{"type":"subscription","vendor":"Notion",...}\' | python ingest.py --stdin')
            print('  python ingest.py \'[{"type":"one_time","item":"Monitor",...}]\'')
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
        result = process_expenses(expenses)
        print(result)

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
