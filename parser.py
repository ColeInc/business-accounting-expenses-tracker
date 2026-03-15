import json
from datetime import datetime
from typing import List, Dict, Any
from anthropic import Anthropic
from config import config


def parse_expense(user_input: str) -> List[Dict[str, Any]]:
    """
    Parse expense input using Claude API
    Returns a list of parsed expenses (can be multiple from one input)
    """

    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    current_date = datetime.now().strftime('%m/%d/%Y')

    prompt = f"""You are a business expense parser. Given the following input, extract the expense details into structured JSON.

Determine if this is a RECURRING subscription or a ONE-TIME purchase.

For RECURRING subscriptions, return:
{{
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
  "cancellation_notice_days": 0,
  "notes": "..."
}}

Valid subscription categories: {', '.join(config.SUBSCRIPTION_CATEGORIES)}

For ONE-TIME purchases, return:
{{
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
}}

Valid one-time categories: {', '.join(config.ONE_TIME_CATEGORIES)}

IMPORTANT RULES:
1. If multiple expenses are present, return an array of objects
2. Today's date is {current_date}. If the user says "today" or "just now", use today's date
3. If a field cannot be determined, use an empty string or 0 for numbers
4. For billing_cycle, ONLY use: Monthly, Annual, or Quarterly
5. For monthly_cost: If annual is given, divide by 12. If quarterly, divide by 3.
6. For amounts, strip currency symbols (return just the number)
7. If expense type is ambiguous, default to "one_time" and add a note
8. Return ONLY valid JSON, no other text

Input:
{user_input}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Try to extract JSON from response
        # Sometimes Claude wraps JSON in markdown code blocks
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()

        parsed = json.loads(response_text)

        # Ensure we return a list
        if isinstance(parsed, dict):
            return [parsed]
        return parsed

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse expense: Invalid JSON response from Claude: {e}")
    except Exception as e:
        raise ValueError(f"Failed to parse expense: {e}")


def format_expense_summary(expense: Dict[str, Any]) -> str:
    """Format a parsed expense for user confirmation"""
    expense_type = expense.get('type', 'unknown')

    if expense_type == 'subscription':
        return f"""
Vendor: {expense.get('vendor', 'N/A')}
Plan: {expense.get('plan_tier', 'N/A')} ({expense.get('billing_cycle', 'N/A')})
Cost: ${expense.get('monthly_cost', 0):.2f}/mo
Started: {expense.get('start_date', 'N/A')}
Payment: {expense.get('payment_method', 'N/A')}
Auto-Renew: {expense.get('auto_renew', 'No')}
""".strip()

    elif expense_type == 'one_time':
        return f"""
Item: {expense.get('item', 'N/A')}
Vendor: {expense.get('vendor', 'N/A')}
Amount: ${expense.get('amount', 0):.2f}
Date: {expense.get('purchase_date', 'N/A')}
Payment: {expense.get('payment_method', 'N/A')}
Tax Deductible: {expense.get('tax_deductible', 'No')}
""".strip()

    return str(expense)
