import os
from dotenv import load_dotenv

load_dotenv()

OP_WEB_BASE_URL = "https://project.apollo.com.ph"
OP_BASE_URL = "https://project.apollo.com.ph/api/v3"
OP_API_TOKEN = os.getenv("OP_API_TOKEN", "")
OP_PROJECT_IDENTIFIER = "payconnect-switch"
OP_PROJECT_ID = 364
OP_BUG_TYPE_ID = 7
OP_NEXT_SPRINT_VERSION_ID = 2036
OP_BACKLOGS_URL = f"{OP_WEB_BASE_URL}/projects/{OP_PROJECT_IDENTIFIER}/backlogs"

RT_USERNAME = os.getenv("RT_USERNAME", "")
RT_PASSWORD = os.getenv("RT_PASSWORD", "")
RT_LOGIN_URL = "https://rt1.apolloglobal.net/"
TARGET_QUEUE = "Apollo SD - Fintech Internal"

CUSTOM_FIELDS = {
    "CustomField-39-Values": "RT",
    "CustomField-40-Values": "Testing",
    "CustomField-41-Values": "Internal",
    "CustomField-42-Values": "New Merchant",
    "CustomField-61-Values": "P1: 12 hours",
}

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
SHEET_TAB_NAME = os.getenv("SHEET_TAB_NAME", "Sheet1")

# Sheet columns: Title | Steps | Expected | Actual | Environment |
#                OpenProject Link | RT1 Ticket # | Status
COL_TITLE = "A"
COL_STEPS = "B"
COL_EXPECTED = "C"
COL_ACTUAL = "D"
COL_ENVIRONMENT = "E"
COL_OP_LINK = "F"
COL_RT1_TICKET = "G"
COL_STATUS = "H"
FIRST_DATA_ROW = 2
