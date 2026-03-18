#!/usr/bin/env python3
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from config import config
from sheets import SheetsClient
from gmail_client import GmailClient


def load_credentials():
    creds = Credentials.from_authorized_user_file(config.TOKEN_PATH, config.SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(config.TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return creds


def build_html(renewals):
    date_str = datetime.now(ZoneInfo('Pacific/Auckland')).strftime('%A, %B %d, %Y')
    if not renewals:
        return (
            f"<html><body><h2>Subscription Renewals</h2>"
            f"<p>{date_str}</p>"
            f"<p style='color:green'>No renewals in the next 7 days.</p>"
            f"</body></html>"
        )
    rows = ""
    for r in renewals:
        if r['days_until'] <= 2:
            color = "#dc3545"
        elif r['days_until'] <= 4:
            color = "#ffc107"
        else:
            color = "#28a745"
        rows += (
            f"<tr>"
            f"<td>{r['vendor']}</td>"
            f"<td>{r['plan_tier']}</td>"
            f"<td>{r['billing_cycle']}</td>"
            f"<td>${r['monthly_cost']}/mo</td>"
            f"<td>{r['next_renewal']}</td>"
            f"<td style='background:{color};color:white;text-align:center'><b>{r['days_until']}d</b></td>"
            f"</tr>"
        )
    return f"""<html><body style='font-family:Arial,sans-serif;padding:20px'>
<h2>Subscription Renewals - {date_str}</h2>
<p><b>{len(renewals)}</b> renewal(s) in next 7 days:</p>
<table border='1' cellpadding='8' style='border-collapse:collapse;width:100%'>
<tr style='background:#f8f9fa'>
  <th>Vendor</th><th>Plan</th><th>Cycle</th><th>Cost</th><th>Renewal Date</th><th>Days Left</th>
</tr>
{rows}
</table>
<p style='font-size:12px;color:#666;margin-top:20px'>Automated reminder from Business Expense Tracker.</p>
</body></html>"""


def main():
    creds = load_credentials()
    sheets = SheetsClient()
    renewals = sheets.get_upcoming_renewals(7)
    print(f"Found {len(renewals)} upcoming renewal(s)")
    if renewals:
        subject = f"Subscription Reminder: {len(renewals)} renewal(s) this week"
    else:
        subject = "Subscription Reminder: No renewals this week"
    GmailClient(creds).send_email(
        to=config.REMINDER_EMAIL,
        subject=subject,
        body_html=build_html(renewals),
    )
    print("Email sent.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
