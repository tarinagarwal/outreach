import os
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

logger = logging.getLogger(__name__)

# Scopes required for Google Docs API
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']


class GoogleDocsService:
    """Service for interacting with Google Docs API"""
    
    def __init__(self):
        self.document_id = os.environ.get('GOOGLE_DOCS_DOCUMENT_ID')
        
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
                logger.warning("Google Docs credentials not configured. Please set up OAuth.")
                self.service = None
                return
        
        self.service = build('docs', 'v1', credentials=self.creds)
    
    def _load_credentials(self):
        """Load credentials from token file"""
        token_path = os.environ.get('GOOGLE_TOKEN_FILE', 'token.json')
        if os.path.exists(token_path):
            return Credentials.from_authorized_user_file(token_path, SCOPES)
        return None
    
    def test_connection(self):
        """Test Google Docs API connection"""
        if not self.service:
            raise Exception("Google Docs service not initialized. Please configure credentials.")
        
        try:
            if not self.document_id:
                raise Exception("GOOGLE_DOCS_DOCUMENT_ID not configured")
            
            # Try to read the document
            doc = self.service.documents().get(documentId=self.document_id).execute()
            return True
        except HttpError as e:
            raise Exception(f"Google Docs connection failed: {str(e)}")
    
    def get_document(self) -> str:
        """Get the full content of a Google Doc"""
        if not self.service or not self.document_id:
            raise Exception("Google Docs service not configured")
        
        try:
            doc = self.service.documents().get(documentId=self.document_id).execute()
            
            # Extract text content from the document
            content = doc.get('body', {}).get('content', [])
            text_parts = []
            
            for element in content:
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for para_element in paragraph.get('elements', []):
                        if 'textRun' in para_element:
                            text_parts.append(para_element['textRun'].get('content', ''))
            
            return '\n'.join(text_parts)
            
        except HttpError as e:
            logger.error(f"Error fetching document: {str(e)}")
            raise Exception(f"Failed to fetch document: {str(e)}")

