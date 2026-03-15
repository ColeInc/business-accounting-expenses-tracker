from typing import Dict, Any


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
