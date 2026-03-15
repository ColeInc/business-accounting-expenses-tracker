#!/usr/bin/env python3
"""
Expense Ingestion Tool - Main Entry Point
Parses expense input and adds to Google Sheets
"""

import sys
from parser import parse_expense, format_expense_summary
from validator import validate_subscription, validate_one_time
from sheets import SheetsClient
from models import Subscription, OneTimePurchase
from config import config


def process_expense(user_input: str) -> str:
    """
    Process expense input end-to-end
    Returns a summary message
    """
    results = []

    try:
        # Parse the input using Claude
        expenses = parse_expense(user_input)

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
                sub = Subscription(**validated)
                sheets.append_subscription(sub)

                summary = format_expense_summary(validated)
                results.append(f"✅ Logged to Subscriptions:\n{summary}")

            elif expense_type == 'one_time':
                # Validate and insert one-time purchase
                validated = validate_one_time(expense)
                purchase = OneTimePurchase(**validated)
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
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<expense description>\"")
        print("\nExamples:")
        print('  python main.py "Notion Plus $10/mo started today"')
        print('  python main.py "Bought a monitor from Dell for $599"')
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    result = process_expense(user_input)
    print(result)


if __name__ == "__main__":
    main()
