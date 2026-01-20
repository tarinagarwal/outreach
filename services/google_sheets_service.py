import os
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

logger = logging.getLogger(__name__)

# Scopes required for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


class GoogleSheetsService:
    """Service for interacting with Google Sheets API"""
    
    def __init__(self):
        self.document_id = os.environ.get('GOOGLE_SHEETS_DOCUMENT_ID')
        self.sheet_id = os.environ.get('GOOGLE_SHEETS_SHEET_ID', '0')  # Default to first sheet
        
        # Try to get credentials from environment variable (JSON string)
        creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                self.creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
            except:
                self.creds = None
        else:
            # Try to load from token file
            self.creds = self._load_credentials()
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                logger.warning("Google Sheets credentials not configured. Please set up OAuth.")
                self.service = None
                return
        
        self.service = build('sheets', 'v4', credentials=self.creds)
    
    def _load_credentials(self):
        """Load credentials from token file"""
        token_path = os.environ.get('GOOGLE_TOKEN_FILE', 'token.json')
        if os.path.exists(token_path):
            return Credentials.from_authorized_user_file(token_path, SCOPES)
        return None
    
    def test_connection(self):
        """Test Google Sheets API connection"""
        if not self.service:
            raise Exception("Google Sheets service not initialized. Please configure credentials.")
        
        try:
            if not self.document_id:
                raise Exception("GOOGLE_SHEETS_DOCUMENT_ID not configured")
            
            # Try to read a single cell
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.document_id,
                range='A1'
            ).execute()
            return True
        except HttpError as e:
            raise Exception(f"Google Sheets connection failed: {str(e)}")
    
    def get_row_by_index(self, row_index: int) -> dict:
        """Get a row from Google Sheets by index (1-based)"""
        if not self.service or not self.document_id:
            raise Exception("Google Sheets service not configured")
        
        try:
            # First, get the header row to know column names
            header_range = f'A1:Z1'
            header_result = self.service.spreadsheets().values().get(
                spreadsheetId=self.document_id,
                range=header_range
            ).execute()
            
            headers = header_result.get('values', [[]])[0] if header_result.get('values') else []
            
            # Get the specific row
            row_range = f'A{row_index}:Z{row_index}'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.document_id,
                range=row_range
            ).execute()
            
            values = result.get('values', [[]])[0] if result.get('values') else []
            
            # Convert to dictionary
            row_data = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    row_data[header] = values[i]
                else:
                    row_data[header] = ''
            
            return row_data
            
        except HttpError as e:
            logger.error(f"Error fetching row {row_index}: {str(e)}")
            raise Exception(f"Failed to fetch row: {str(e)}")

