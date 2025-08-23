import os
import json
import pytz
from datetime import datetime, timedelta
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled, FollowupAction

# Import utility functions from the utils.py file
from utils import get_count, send_reminder, get_config_path

# --- Helper Function for Configuration ---
def load_config():
    """Loads the configuration from config.json, returning config and error."""
    config_path = get_config_path()
    try:
        if not os.path.exists(config_path):
            return None, "Configuration file not found. Please contact the administrator."
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError:
        return None, "Invalid configuration file format. Please contact the administrator."
    except Exception as e:
        return None, f"An unexpected error occurred while loading config: {str(e)}"

class ActionTrackForm(Action):
    def name(self):
        return "action_track_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        sender_id = tracker.sender_id
        # Note: Consider moving allowed_users to an environment variable for flexibility
        allowed_users = os.environ.get('ALLOWED_USER_IDS', '1301082863').split(',')
        if sender_id not in allowed_users:
            dispatcher.utter_message(text="You are not authorized to perform this action.")
            return []

        sheet_id = next(tracker.get_latest_entity_values("sheet_id"), None)
        if not sheet_id:
            dispatcher.utter_message(text="Please provide the sheet ID.")
            return []
            
        config, error = load_config()
        if error:
            dispatcher.utter_message(text=error)
            return []
        
        try:
            config['current_sheet_id'] = sheet_id
            config['current_form_id'] = None  # Reset form_id when tracking a new sheet
            
            # Ensure master_sheet_id has a default if it's missing
            if 'master_sheet_id' not in config or not config.get('master_sheet_id'):
                config['master_sheet_id'] = os.environ.get('MASTER_SHEET_ID', 'default_master_sheet_id_here')

            with open(get_config_path(), 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            dispatcher.utter_message(text=f"Now tracking the form with sheet ID {sheet_id}.")
        except Exception as e:
            dispatcher.utter_message(text=f"Failed to set tracking: {str(e)}. Please try again.")
        
        return []

class ActionGetCount(Action):
    def name(self):
        return "action_get_count"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        config, error = load_config()
        if error:
            dispatcher.utter_message(text=error)
            return []

        sheet_id = config.get('current_sheet_id')
        if not sheet_id:
            dispatcher.utter_message(text="No form or sheet is currently being tracked.")
            return []
        
        try:
            count = get_count(sheet_id)
            dispatcher.utter_message(text=f"Currently, {count} out of 26 have filled the form.")
        except Exception as e:
            dispatcher.utter_message(text=f"Failed to get the count: {str(e)}. Please try again later.")
        
        return []

class ActionSendReminder(Action):
    def name(self):
        return "action_send_reminder"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        config, error = load_config()
        if error:
            dispatcher.utter_message(text=error)
            return []

        sheet_id = config.get("current_sheet_id")
        if not sheet_id:
            dispatcher.utter_message(text="No form or sheet is currently being tracked.")
            return []
        
        try:
            result = send_reminder(sheet_id)
            dispatcher.utter_message(text=result)
        except Exception as e:
            dispatcher.utter_message(text=f"Error sending reminder: {e}")
            return []

        # Schedule the next reminder
        tz = pytz.timezone("Asia/Kolkata")
        reminder_time = datetime.now(tz) + timedelta(minutes=10)
        reminder_name = f"form_reminder_{int(datetime.now().timestamp())}"

        return [ReminderScheduled(
            "EXTERNAL_form_reminder",
            trigger_date_time=reminder_time,
            name=reminder_name,
            kill_on_user_message=False
        )]
        
class ActionFormReminder(Action):
    def name(self):
        return "action_form_reminder"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        return [FollowupAction("action_send_reminder")]

class ActionCheckCurrentForm(Action):
    def name(self):
        return "action_check_current_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        config, error = load_config()
        if error:
            dispatcher.utter_message(text=error)
            return []

        form_id = config.get('current_form_id', 'Not set')
        sheet_id = config.get('current_sheet_id', 'Not set')
        
        dispatcher.utter_message(text=f"Currently tracking form ID: {form_id}, sheet ID: {sheet_id}.")
        return []