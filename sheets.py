import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import config
from models import Subscription, OneTimePurchase
from typing import List


class SheetsClient:
    """Google Sheets API client"""

    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API using OAuth"""
        # Token file stores the user's access and refresh tokens
        if os.path.exists(config.TOKEN_PATH):
            self.creds = Credentials.from_authorized_user_file(
                config.TOKEN_PATH,
                config.SCOPES
            )

        # If there are no valid credentials, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_PATH,
                    config.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(config.TOKEN_PATH, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('sheets', 'v4', credentials=self.creds)

    def append_subscription(self, subscription: Subscription) -> dict:
        """Append a subscription to the Subscriptions tab"""
        try:
            values = [subscription.to_row()]
            body = {'values': values}

            result = self.service.spreadsheets().values().append(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f'{config.SUBSCRIPTIONS_TAB}!A:P',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return result

        except HttpError as e:
            raise Exception(f"Failed to append subscription: {e}")

    def append_one_time(self, purchase: OneTimePurchase) -> dict:
        """Append a one-time purchase to the One-Time Purchases tab"""
        try:
            values = [purchase.to_row()]
            body = {'values': values}

            result = self.service.spreadsheets().values().append(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f'{config.ONE_TIME_TAB}!A:J',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return result

        except HttpError as e:
            raise Exception(f"Failed to append one-time purchase: {e}")

    def get_subscriptions(self) -> List[List]:
        """Read all subscriptions from the sheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f'{config.SUBSCRIPTIONS_TAB}!A:P'
            ).execute()

            return result.get('values', [])

        except HttpError as e:
            raise Exception(f"Failed to read subscriptions: {e}")

    def get_one_time_purchases(self) -> List[List]:
        """Read all one-time purchases from the sheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f'{config.ONE_TIME_TAB}!A:J'
            ).execute()

            return result.get('values', [])

        except HttpError as e:
            raise Exception(f"Failed to read one-time purchases: {e}")

    def append_log(self, invoice_name: str, datetime_nzt: str, description: str,
                   is_recurring: bool, sheet_appended: str) -> dict:
        """Append a processing log entry to the Logs tab"""
        try:
            values = [[
                invoice_name,
                datetime_nzt,
                description,
                "Yes" if is_recurring else "No",
                sheet_appended
            ]]
            body = {'values': values}

            result = self.service.spreadsheets().values().append(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f'{config.LOGS_TAB}!A:E',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return result

        except HttpError as e:
            raise Exception(f"Failed to append log: {e}")

    def ensure_logs_sheet_exists(self):
        """Create the Logs sheet if it doesn't exist, with headers"""
        try:
            # Get existing sheets
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=config.SPREADSHEET_ID
            ).execute()

            existing_sheets = [s['properties']['title'] for s in spreadsheet['sheets']]

            if config.LOGS_TAB not in existing_sheets:
                # Create the sheet
                request = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': config.LOGS_TAB
                            }
                        }
                    }]
                }
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=config.SPREADSHEET_ID,
                    body=request
                ).execute()

                # Add headers
                headers = [['Invoice Name', 'Date/Time (NZT)', 'Description', 'Recurring?', 'Sheet Appended']]
                self.service.spreadsheets().values().update(
                    spreadsheetId=config.SPREADSHEET_ID,
                    range=f'{config.LOGS_TAB}!A1:E1',
                    valueInputOption='USER_ENTERED',
                    body={'values': headers}
                ).execute()

                return True
            return False

        except HttpError as e:
            raise Exception(f"Failed to ensure logs sheet: {e}")
