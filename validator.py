import re
from datetime import datetime
from typing import Dict, Any
from config import config


def validate_category(category: str, expense_type: str) -> str:
    """Validate and map category to allowed values"""
    if expense_type == 'subscription':
        valid_categories = config.SUBSCRIPTION_CATEGORIES
    else:
        valid_categories = config.ONE_TIME_CATEGORIES

    # Case-insensitive match
    for valid_cat in valid_categories:
        if category.lower() == valid_cat.lower():
            return valid_cat

    # If no match, return Other
    return 'Other'


def validate_billing_cycle(cycle: str) -> str:
    """Validate billing cycle"""
    for valid_cycle in config.BILLING_CYCLES:
        if cycle.lower() == valid_cycle.lower():
            return valid_cycle
    return 'Monthly'


def validate_date(date_str: str) -> str:
    """Validate and format date as DD/MM/YYYY (NZ locale, matches sheet format)"""
    if not date_str:
        return ''

    # Try to parse various date formats
    formats = [
        '%d/%m/%Y', '%d-%m-%Y',
        '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d',
        '%B %d, %Y', '%b %d, %Y', '%Y/%m/%d'
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%d/%m/%Y')
        except ValueError:
            continue

    # If parsing fails, return original
    return date_str


def validate_amount(amount: Any) -> float:
    """Validate and clean dollar amount"""
    if isinstance(amount, (int, float)):
        return abs(float(amount))

    if isinstance(amount, str):
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$,\s]', '', amount)
        try:
            return abs(float(cleaned))
        except ValueError:
            return 0.0

    return 0.0


def validate_yes_no(value: str) -> str:
    """Validate Yes/No fields"""
    if not value:
        return 'No'

    value_lower = value.lower()
    if value_lower in ['yes', 'y', 'true', '1']:
        return 'Yes'
    return 'No'


def validate_subscription(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean subscription data"""
    validated = data.copy()

    # Validate category
    validated['category'] = validate_category(
        validated.get('category', 'Other'),
        'subscription'
    )

    # Validate billing cycle
    validated['billing_cycle'] = validate_billing_cycle(
        validated.get('billing_cycle', 'Monthly')
    )

    # Validate dates
    validated['start_date'] = validate_date(validated.get('start_date', ''))
    validated['contract_end'] = validate_date(validated.get('contract_end', ''))

    # Validate amounts
    validated['monthly_cost'] = validate_amount(validated.get('monthly_cost', 0))

    # Validate Yes/No fields
    validated['auto_renew'] = validate_yes_no(validated.get('auto_renew', 'No'))

    # Apply defaults
    if not validated.get('payment_method'):
        validated['payment_method'] = config.DEFAULT_PAYMENT_METHOD

    if not validated.get('account_email'):
        validated['account_email'] = config.DEFAULT_ACCOUNT_EMAIL

    if not validated.get('currency'):
        validated['currency'] = 'USD'

    return validated


def validate_one_time(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean one-time purchase data"""
    validated = data.copy()

    # Validate category
    validated['category'] = validate_category(
        validated.get('category', 'Other'),
        'one_time'
    )

    # Validate dates
    validated['purchase_date'] = validate_date(validated.get('purchase_date', ''))
    validated['warranty_until'] = validate_date(validated.get('warranty_until', ''))

    # Validate amounts
    validated['amount'] = validate_amount(validated.get('amount', 0))

    # Validate Yes/No fields
    validated['tax_deductible'] = validate_yes_no(validated.get('tax_deductible', 'No'))
    validated['receipt_saved'] = validate_yes_no(validated.get('receipt_saved', 'No'))

    # Apply defaults
    if not validated.get('payment_method'):
        validated['payment_method'] = config.DEFAULT_PAYMENT_METHOD

    return validated
