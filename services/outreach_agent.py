import logging
import json
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class OutreachAgent:
    """Main outreach agent that orchestrates the workflow"""
    
    def __init__(self, sheets_service, docs_service, ai_service, email_service):
        self.sheets_service = sheets_service
        self.docs_service = docs_service
        self.ai_service = ai_service
        self.email_service = email_service
        
        # Prompt template from n8n workflow
        self.prompt_template = """You are an automation outreach agent.
Follow all instructions EXACTLY.

Do NOT explain, do NOT summarize, and do NOT ask questions.
Your ONLY job is to output the required JSON fields. Nothing else.

────────────────────────────────────────
COMPANY DATA (JSON INPUT)

Use this company row EXACTLY as provided:

{company_data}

This JSON contains the target company details, including the field:
"email_to_use"

────────────────────────────────────────
STEP 1 — Fetch Our Company's Knowledgebase

Call the tool:
→ "Get a document in Google Docs"

Return the raw tool output EXACTLY as received.

Use ONLY:
• Our Company's Knowledgebase
• The provided company row

to generate the outreach email.

────────────────────────────────────────
STEP 2 — Generate Outreach Email Content

You MUST generate:

1. **to**
   - Must be the EXACT value of "email_to_use" from the input JSON.

2. **subject**
   - A unique, compelling subject line.
   - Personalized to the individual or company.
   - Must be a rewritten variation of ONE of these patterns:
        • Quick idea for {CompanyName}
        • {Name}, spotted something you can automate
        • Boosting {Industry} performance at {CompanyName}
        • A smarter way to cut costs at {CompanyName}
        • {Name}, this can save your team 10–20 hrs/week

3. **emailBody**
   - A polished, professional HTML outreach email.
   - Use this as inspiration:

Hi {FirstName},

I came across {CompanyName} and noticed the work you're doing in the {Industry} space.
I also noticed a few areas on your website where automation can dramatically improve efficiency and reduce workload.

Based on what companies in {Industry} typically struggle with, here are several areas we can automate immediately:
• Provide 3–6 customized, industry-specific pain points  
  (strictly derived from the our Company's Knowledgebase)

This is exactly what we do at our company.
We build done-for-you automation systems using:
AI Voice Agents, Chat & Email Automation, n8n workflows, CRM integrations, and smart data processing tools — reducing operational time & costs by 70–90%.

To help you identify hidden inefficiencies, we're offering a free 1:1 Automation Consultation.
We'll personally review your systems at {CompanyName}, map where you're losing time and money, and show you how to automate everything step-by-step.

If you're open to it, reply "Yes" and I'll send available times for a quick call.

Do NOT add any signature, sign-off, closing line, name, or regards.
End the email immediately after the final sentence.

────────────────────────────────────────
STEP 3 — OUTPUT FORMAT (STRICT)

Your final output MUST be a valid JSON object that EXACTLY matches this structure:

{{
  "to": "<email_to_use>",
  "subject": "<generated subject>",
  "emailBody": "<generated HTML email>"
}}

RULES (VERY IMPORTANT):
• Do NOT wrap the JSON in quotes.
• Do NOT escape characters.
• Do NOT add backticks.
• Do NOT add extra keys.
• Do NOT output anything before or after the JSON object.
• Output ONLY the JSON object.

────────────────────────────────────────
GLOBAL RULES (STRICT)

• Use ONLY "email_to_use" as the recipient field.
• Never mention validation logic.
• Never mention tools or automation steps.
• Never modify Our Company's Knowledgebase.
• Output ONLY:
    - to  
    - subject  
    - emailBody
"""
    
    def execute(self, start_row: int, end_row: int) -> Dict[str, Any]:
        """Execute the outreach workflow for the given row range"""
        results = {
            'processed': 0,
            'sent': 0,
            'skipped': 0,
            'errors': [],
            'details': []
        }
        
        # Get knowledge base once
        try:
            knowledge_base = self.docs_service.get_document()
            logger.info("Knowledge base fetched successfully")
        except Exception as e:
            logger.error(f"Error fetching knowledge base: {str(e)}")
            results['errors'].append(f"Knowledge base error: {str(e)}")
            return results
        
        # Process each row
        for row_index in range(start_row, end_row + 1):
            try:
                logger.info(f"Processing row {row_index}")
                
                # Fetch company data from Google Sheets
                company_data = self.sheets_service.get_row_by_index(row_index)
                
                if not company_data:
                    logger.warning(f"No data found for row {row_index}")
                    results['skipped'] += 1
                    continue
                
                # Validate email
                email_to_use = company_data.get('email_to_use', '')
                if not email_to_use or '@' not in email_to_use:
                    logger.warning(f"Invalid email for row {row_index}: {email_to_use}")
                    results['skipped'] += 1
                    results['details'].append({
                        'row': row_index,
                        'status': 'skipped',
                        'reason': 'Invalid email'
                    })
                    continue
                
                # Generate email using AI
                email_content = self._generate_email(company_data, knowledge_base)
                
                if not email_content:
                    logger.error(f"Failed to generate email for row {row_index}")
                    results['errors'].append(f"Row {row_index}: Email generation failed")
                    continue
                
                # Send email
                self.email_service.send_email(
                    email_content['to'],
                    email_content['subject'],
                    email_content['emailBody']
                )
                
                results['sent'] += 1
                results['details'].append({
                    'row': row_index,
                    'status': 'sent',
                    'to': email_content['to'],
                    'subject': email_content['subject']
                })
                
                logger.info(f"Email sent successfully for row {row_index}")
                
            except Exception as e:
                logger.error(f"Error processing row {row_index}: {str(e)}")
                results['errors'].append(f"Row {row_index}: {str(e)}")
            
            results['processed'] += 1
        
        return results
    
    def _generate_email(self, company_data: Dict, knowledge_base: str) -> Dict[str, str]:
        """Generate email content using AI"""
        # Format company data as JSON string
        company_data_str = json.dumps(company_data, indent=2)
        
        # Build the prompt
        prompt = self.prompt_template.format(company_data=company_data_str)
        
        # Add knowledge base to context
        full_prompt = f"{prompt}\n\nKNOWLEDGE BASE:\n{knowledge_base}"
        
        # Call AI service
        response = self.ai_service.generate_email(full_prompt)
        
        # Parse JSON response
        try:
            # Clean response - remove markdown code blocks if present
            response_clean = response.strip()
            if response_clean.startswith('```'):
                # Remove markdown code block
                lines = response_clean.split('\n')
                response_clean = '\n'.join(lines[1:-1])
            
            email_content = json.loads(response_clean)
            
            # Validate required fields
            if 'to' in email_content and 'subject' in email_content and 'emailBody' in email_content:
                return email_content
            else:
                logger.error("AI response missing required fields")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.error(f"Response was: {response[:500]}")
            return None

