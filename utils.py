import gspread
import os
import requests
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- Secure Configuration ---
# Load secrets from environment variables
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

# --- Path Configuration ---
# Assumes 'credentials.json' and 'config.json' are in a 'config' directory
# at the same level as your 'actions' directory.
def get_config_path(filename="config.json"):
    """Constructs a relative path to a config file."""
    return os.path.join(os.path.dirname(__file__), '..', 'config', filename)

# --- Google API Initialization ---
try:
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/forms']
    credentials_path = get_config_path("credentials.json")
    creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
    sheets_client = gspread.authorize(creds)
    forms_service = build('forms', 'v1', credentials=creds)
except FileNotFoundError:
    print(f"ERROR: credentials.json not found at {credentials_path}. Please check the path.")
    # Exit or handle the error gracefully if credentials are not found
    sheets_client = None
    forms_service = None
except Exception as e:
    print(f"ERROR: Failed to initialize Google services: {e}")
    sheets_client = None
    forms_service = None

def get_count(sheet_id):
    """Get the number of form submissions."""
    if not sheet_id:
        raise ValueError("No sheet_id provided.")
    if not sheets_client:
        raise ConnectionError("Google Sheets client is not initialized.")
    
    spreadsheet = sheets_client.open_by_key(sheet_id)
    sheet = spreadsheet.sheet1
    records = sheet.get_all_records()
    return len(records)
    
def get_not_filled_students(master_sheet_id, form_sheet_id):
    """Compare master sheet with form responses and return missing students."""
    if not sheets_client:
        raise ConnectionError("Google Sheets client is not initialized.")
        
    master_sheet = sheets_client.open_by_key(master_sheet_id).sheet1
    master_records = master_sheet.get_all_records()

    form_sheet = sheets_client.open_by_key(form_sheet_id).sheet1
    form_records = form_sheet.get_all_records()

    master_rolls = {str(row["Roll"]): row["Name"] for row in master_records if "Roll" in row and "Name" in row}
    filled_rolls = {str(row["Roll"]) for row in form_records if "Roll" in row}

    missing = {roll: name for roll, name in master_rolls.items() if roll not in filled_rolls}
    total_count = len(master_rolls)
    filled_count = len(filled_rolls)
    return missing, filled_count, total_count
    
def send_reminder(sheet_id):
    """Send Telegram reminder with missing students list."""
    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.")
    if not sheet_id:
        raise ValueError("No sheet_id provided.")

    with open(get_config_path(), "r", encoding="utf-8") as f:
        config = json.load(f)
    master_sheet_id = config.get("master_sheet_id")

    if not master_sheet_id:
        raise ValueError("Master sheet ID not configured in config.json.")

    missing, filled_count, total_count = get_not_filled_students(master_sheet_id, sheet_id)

    if not missing:
        message = f"✅ All {total_count} students have filled the form."
    else:
        message_lines = [f"📊 {filled_count} out of {total_count} students have filled the form."]
        message_lines.append("\n⚠️ The following students have not filled the form:")
        for roll, name in missing.items():
            message_lines.append(f"{roll} - {name}")
        message = "\n".join(message_lines)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

    return "Reminder sent with missing students list."

# (Other utility functions like get_linked_sheet_id can remain the same)