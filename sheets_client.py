import gspread
from google.oauth2.service_account import Credentials

import config

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetsClient:
    def __init__(self):
        creds = Credentials.from_service_account_file(
            config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(config.GOOGLE_SHEET_ID)
        self.ws = sh.worksheet(config.SHEET_TAB_NAME)

    def get_pending_rows(self):
        all_values = self.ws.get_all_values()
        pending = []

        for idx, row in enumerate(all_values[config.FIRST_DATA_ROW - 1:], start=config.FIRST_DATA_ROW):
            row = row + [""] * (8 - len(row))
            title = row[0].strip()
            status = row[7].strip()

            if title and not status:
                pending.append({
                    "row_number": idx,
                    "title": title,
                    "steps": row[1].strip(),
                    "expected": row[2].strip(),
                    "actual": row[3].strip(),
                    "environment": row[4].strip(),
                })

        return pending

    def mark_row_complete(self, row_number, op_link, rt1_ticket):
        self.ws.update_acell(f"{config.COL_OP_LINK}{row_number}", op_link)
        self.ws.update_acell(f"{config.COL_RT1_TICKET}{row_number}", str(rt1_ticket))
        self.ws.update_acell(f"{config.COL_STATUS}{row_number}", "Done")

    def mark_row_failed(self, row_number, error_message):
        self.ws.update_acell(f"{config.COL_STATUS}{row_number}", f"Failed: {error_message[:80]}")
