import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


class GoogleSheetsService:

    def __init__(self, credentials_path="credentials/credentials.json"):
        # On Render: read from environment variable
        # On local: read from credentials file
        google_creds_env = os.environ.get("GOOGLE_CREDENTIALS")

        if google_creds_env:
            creds_dict = json.loads(google_creds_env)
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )

        self.client = gspread.authorize(creds)

    def open_spreadsheet(self, name):
        return self.client.open(name)

    def get_registration_data(self, spreadsheet_name):
        spreadsheet = self.open_spreadsheet(spreadsheet_name)
        sheet = spreadsheet.worksheet("Form Responses 1")
        return sheet.get_all_records()

    def get_existing_timestamps(self, spreadsheet_name):
        spreadsheet = self.open_spreadsheet(spreadsheet_name)
        sheet = spreadsheet.worksheet("Passes")
        records = sheet.get_all_records()
        return set(str(row["Timestamp"]) for row in records)

    def append_passes(self, spreadsheet_name, rows):
        spreadsheet = self.open_spreadsheet(spreadsheet_name)
        sheet = spreadsheet.worksheet("Passes")
        sheet.append_rows(rows)
        return len(rows)