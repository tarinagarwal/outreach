import os
import logging
from openai import OpenAI
import json

logger = logging.getLogger(__name__)


class AIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
        self.client = None
        
        if not self.api_key:
            logger.warning("OpenAI API key not configured. AI features will not work.")
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {str(e)}. AI features will not work.")
                self.client = None
    
    def _get_client(self):
        """Get or create OpenAI client"""
        if not self.api_key:
            raise Exception("OpenAI API key not configured")
        if not self.client:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                raise Exception(f"Failed to initialize OpenAI client: {str(e)}")
        return self.client
    
    def test_connection(self):
        """Test OpenAI API connection"""
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Say 'test successful' if you can read this."}
                ],
                max_tokens=10
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI connection failed: {str(e)}")
    
    def generate_email(self, prompt: str) -> str:
        """Generate email content using OpenAI"""
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an automation outreach agent. Output only valid JSON without any additional text, explanations, or markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # If response_format is json_object, OpenAI wraps it, so we need to parse and extract
            try:
                parsed = json.loads(content)
                # If it's already in the correct format, return as JSON string
                if 'to' in parsed and 'subject' in parsed and 'emailBody' in parsed:
                    return json.dumps(parsed)
                return content
            except:
                return content
                
        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            raise Exception(f"Failed to generate email: {str(e)}")

