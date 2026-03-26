from dataclasses import dataclass
from typing import Optional


@dataclass
class Subscription:
    """Represents a recurring subscription expense"""
    vendor: str
    category: str
    plan_tier: str = ""
    billing_cycle: str = ""  # Monthly, Annual, Quarterly
    monthly_cost: float = 0.0
    currency: str = "USD"
    start_date: str = ""
    auto_renew: str = "No"
    payment_method: str = ""
    account_email: str = ""
    contract_end: str = ""
    cancellation_notice_days: str = ""
    notes: str = ""

    def to_row(self) -> list:
        """Convert to a row for Google Sheets (columns A-Q)
        A: Vendor, B: Category, C: Plan Tier, D: Billing Cycle,
        E: Monthly Cost, F: Annual Cost (auto), G: Currency,
        H: Start Date, I: Next Renewal (auto), J: Days Until Renewal (auto),
        K: Auto-Renew, L: Payment Method, M: Account Email,
        N: Contract End, O: Cancellation Notice (Days), P: Cancel By Date (auto),
        Q: Notes
        """
        return [
            self.vendor,
            self.category,
            self.plan_tier,
            self.billing_cycle,
            self.monthly_cost,
            '',  # F: Annual Cost - auto-calculated
            self.currency,
            self.start_date,
            '',  # I: Next Renewal - auto-calculated
            '',  # J: Days Until Renewal - auto-calculated
            self.auto_renew,
            self.payment_method,
            self.account_email,
            self.contract_end,
            self.cancellation_notice_days,
            '',  # P: Cancel By Date - auto-calculated
            self.notes,
        ]


@dataclass
class OneTimePurchase:
    """Represents a one-time purchase expense"""
    item: str
    category: str
    vendor: str = ""
    purchase_date: str = ""
    amount: float = 0.0
    payment_method: str = ""
    tax_deductible: str = "No"
    receipt_saved: str = "No"
    warranty_until: str = ""
    notes: str = ""

    def to_row(self) -> list:
        """Convert to a row for Google Sheets (columns A-J)"""
        return [
            self.item,
            self.category,
            self.vendor,
            self.purchase_date,
            self.amount,
            self.payment_method,
            self.tax_deductible,
            self.receipt_saved,
            self.warranty_until,
            self.notes,
        ]
