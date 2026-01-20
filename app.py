from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import json
from services.email_service import EmailService
from services.google_sheets_service import GoogleSheetsService
from services.google_docs_service import GoogleDocsService
from services.ai_service import AIService
from services.outreach_agent import OutreachAgent
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
email_service = EmailService()
sheets_service = GoogleSheetsService()
docs_service = GoogleDocsService()
ai_service = AIService()
outreach_agent = OutreachAgent(sheets_service, docs_service, ai_service, email_service)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = {
        'google_sheets_document_id': os.environ.get('GOOGLE_SHEETS_DOCUMENT_ID', ''),
        'google_sheets_sheet_id': os.environ.get('GOOGLE_SHEETS_SHEET_ID', ''),
        'google_docs_document_id': os.environ.get('GOOGLE_DOCS_DOCUMENT_ID', ''),
        'smtp_from_email': os.environ.get('SMTP_FROM_EMAIL', ''),
        'openai_model': os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
    }
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    data = request.json
    # In production, save to database or config file
    # For now, we'll use environment variables
    return jsonify({'status': 'success', 'message': 'Configuration updated'})


@app.route('/api/execute', methods=['POST'])
def execute_workflow():
    """Execute the outreach workflow"""
    try:
        data = request.json
        start_row = int(data.get('startRow', 1))
        end_row = int(data.get('endRow', 10))
        
        logger.info(f"Starting workflow execution: rows {start_row} to {end_row}")
        
        # Execute the outreach agent
        results = outreach_agent.execute(start_row, end_row)
        
        return jsonify({
            'status': 'success',
            'message': f'Processed {results["processed"]} rows, sent {results["sent"]} emails',
            'results': results
        })
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email sending"""
    try:
        data = request.json
        to_email = data.get('to')
        subject = data.get('subject', 'Test Email')
        body = data.get('body', 'This is a test email')
        
        email_service.send_email(to_email, subject, body)
        
        return jsonify({'status': 'success', 'message': 'Test email sent'})
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/validate-connection', methods=['POST'])
def validate_connection():
    """Validate API connections"""
    try:
        data = request.json
        service = data.get('service')
        
        results = {}
        
        if service == 'google_sheets' or service == 'all':
            try:
                # Test Google Sheets connection
                sheets_service.test_connection()
                results['google_sheets'] = {'status': 'success'}
            except Exception as e:
                results['google_sheets'] = {'status': 'error', 'message': str(e)}
        
        if service == 'google_docs' or service == 'all':
            try:
                # Test Google Docs connection
                docs_service.test_connection()
                results['google_docs'] = {'status': 'success'}
            except Exception as e:
                results['google_docs'] = {'status': 'error', 'message': str(e)}
        
        if service == 'openai' or service == 'all':
            try:
                # Test OpenAI connection
                ai_service.test_connection()
                results['openai'] = {'status': 'success'}
            except Exception as e:
                results['openai'] = {'status': 'error', 'message': str(e)}
        
        if service == 'smtp' or service == 'all':
            try:
                # Test SMTP connection
                email_service.test_connection()
                results['smtp'] = {'status': 'success'}
            except Exception as e:
                results['smtp'] = {'status': 'error', 'message': str(e)}
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error validating connections: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(debug=True, host='0.0.0.0', port=port)

