import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Google Sheets
    SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID', '')
    CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', './client_secret.json')
    TOKEN_PATH = './token.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


    # Defaults
    DEFAULT_PAYMENT_METHOD = os.getenv('DEFAULT_PAYMENT_METHOD', 'Business Credit Card')
    DEFAULT_ACCOUNT_EMAIL = os.getenv('DEFAULT_ACCOUNT_EMAIL', '')

    # Sheet tab names
    SUBSCRIPTIONS_TAB = 'Subscriptions'
    ONE_TIME_TAB = 'One-Time Purchases'
    LOGS_TAB = 'Logs'

    # Local log file
    LOCAL_LOG_PATH = './expense_processing_log.json'

    # Valid categories
    SUBSCRIPTION_CATEGORIES = [
        'Accounting', 'Analytics', 'Communication', 'CRM', 'Design',
        'Development', 'Hosting', 'Legal', 'Marketing', 'Payroll',
        'Productivity', 'Project Mgmt', 'Security', 'Storage', 'Other'
    ]

    ONE_TIME_CATEGORIES = [
        'Branding', 'Equipment', 'Furniture', 'Legal Fees', 'Licenses',
        'Office Supplies', 'Software License', 'Training', 'Web', 'Other'
    ]

    BILLING_CYCLES = ['Monthly', 'Annual', 'Quarterly']


config = Config()
