"""
Google Sheets Storage
Stores event data in Google Sheets using gspread
"""

from typing import List
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

from src.storage.base_storage import BaseStorage
from src.models.event import Event
from src.utils.config import config
from src.utils.logger import setup_logger
from src.utils.helpers import is_date_expired


logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)


class GoogleSheetsStorage(BaseStorage):
    """Google Sheets storage backend"""
    
    def __init__(self, sheet_id: str = None, credentials_file: str = None):
        """
        Initialize Google Sheets storage
        
        Args:
            sheet_id: Google Sheet ID
            credentials_file: Path to credentials JSON file
        """
        super().__init__()
        self.sheet_id = sheet_id or config.GOOGLE_SHEETS_ID
        self.credentials_file = credentials_file or config.GOOGLE_CREDENTIALS_FILE
        self._client = None
        self._worksheet = None

    def _get_client(self):
        """Authorize and return gspread client"""
        if not self.credentials_file or not self.sheet_id:
            raise ValueError("Google Sheets credentials file and sheet ID must be set")

        if self._client is None:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=scopes)
            self._client = gspread.authorize(creds)
        return self._client

    def _get_worksheet(self):
        """Open sheet and return worksheet"""
        if self._worksheet is None:
            client = self._get_client()
            sheet = client.open_by_key(self.sheet_id)
            try:
                self._worksheet = sheet.worksheet("Events")
            except Exception:
                self._worksheet = sheet.sheet1
        return self._worksheet

    def _ensure_headers(self, worksheet):
        """Ensure header row exists"""
        headers = [
            "Event ID", "Event Name", "Date", "Venue", "City",
            "Category", "URL", "Source", "Status", "Last Updated"
        ]
        try:
            existing = worksheet.row_values(1)
            if existing != headers:
                worksheet.clear()
                worksheet.append_row(headers)
        except Exception:
            worksheet.clear()
            worksheet.append_row(headers)

    def save_events(self, events: List[Event]) -> bool:
        """
        Save events to Google Sheets
        """
        try:
            worksheet = self._get_worksheet()
            self._ensure_headers(worksheet)

            existing_events = self.load_events()
            merged_events = self.merge_events(events, existing_events)

            rows = [event.to_dict() for event in merged_events]
            values = [
                [
                    row["Event ID"], row["Event Name"], row["Date"], row["Venue"], row["City"],
                    row["Category"], row["URL"], row["Source"], row["Status"], row["Last Updated"]
                ]
                for row in rows
            ]

            worksheet.clear()
            worksheet.append_row([
                "Event ID", "Event Name", "Date", "Venue", "City",
                "Category", "URL", "Source", "Status", "Last Updated"
            ])
            if values:
                worksheet.update("A2", values, value_input_option="RAW")

            logger.info(f"Saved {len(merged_events)} events to Google Sheets")
            return True
        except Exception as e:
            logger.error(f"Error saving events to Google Sheets: {e}")
            return False

    def load_events(self) -> List[Event]:
        """
        Load events from Google Sheets
        """
        try:
            worksheet = self._get_worksheet()
            self._ensure_headers(worksheet)
            records = worksheet.get_all_records()
            if not records:
                return []

            events = []
            for row in records:
                try:
                    event = Event(
                        event_name=str(row.get("Event Name", "")),
                        date=str(row.get("Date", "")),
                        venue=str(row.get("Venue", "")),
                        city=str(row.get("City", "")),
                        category=str(row.get("Category", "")),
                        url=str(row.get("URL", "")),
                        source=str(row.get("Source", "")),
                        status=str(row.get("Status", "")),
                        event_id=str(row.get("Event ID", "")),
                    )
                    events.append(event)
                except Exception as e:
                    logger.debug(f"Error parsing Google Sheets row: {e}")
                    continue

            logger.info(f"Loaded {len(events)} events from Google Sheets")
            return events
        except Exception as e:
            logger.error(f"Error loading events from Google Sheets: {e}")
            return []

    def update_event(self, event: Event) -> bool:
        """
        Update existing event
        """
        try:
            events = self.load_events()
            for i, existing_event in enumerate(events):
                if existing_event.event_id == event.event_id:
                    events[i] = event
                    return self.save_events(events)

            events.append(event)
            return self.save_events(events)
        except Exception as e:
            logger.error(f"Error updating event in Google Sheets: {e}")
            return False

    def delete_event(self, event_id: str) -> bool:
        """
        Delete event by ID
        """
        try:
            events = self.load_events()
            events = [e for e in events if e.event_id != event_id]
            return self.save_events(events)
        except Exception as e:
            logger.error(f"Error deleting event from Google Sheets: {e}")
            return False

    def mark_expired_events(self) -> int:
        """
        Mark expired events
        """
        try:
            events = self.load_events()
            expired_count = 0

            for event in events:
                if event.status == "Active" and is_date_expired(event.date, config.MARK_EXPIRED_DAYS):
                    event.status = "Expired"
                    event.last_updated = datetime.now()
                    expired_count += 1

            if expired_count > 0:
                self.save_events(events)
                logger.info(f"Marked {expired_count} events as expired")

            return expired_count
        except Exception as e:
            logger.error(f"Error marking expired events in Google Sheets: {e}")
            return 0
