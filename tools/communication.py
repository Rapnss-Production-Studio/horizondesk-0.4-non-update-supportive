from core.tools import BaseTool
import os
import requests
import json

class SendEmailTool(BaseTool):
    def __init__(self):
        super().__init__("SendEmail", "Sends an email using Brevo/SMTP. Input: 'to', 'subject', 'body'.")

    def execute(self, to=None, subject=None, body=None, payload=None):
        if payload and isinstance(payload, dict):
            to = payload.get('to')
            subject = payload.get('subject')
            body = payload.get('body')
            
        if not to or not subject or not body:
             return "Error: 'to', 'subject', and 'body' correspondings required."

        # BREVO API (Mock/Placeholder logic if no key)
        api_key = os.getenv("BREVO_API_KEY")
        if not api_key:
            return f"[MOCK] Email sent to {to}\nSubject: {subject}\nBody: {body}\n(Configure BREVO_API_KEY in .env for real sending)"

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        data = {
            "sender": {"name": "OmniAgent", "email": "agent@horizon.desk"},
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": f"<p>{body}</p>"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                return f"Email sent successfully to {to}"
            else:
                return f"Error sending email: {response.text}"
        except Exception as e:
            return f"Error: {e}"

class SendSMSTool(BaseTool):
    def __init__(self):
        super().__init__("SendSMS", "Sends an SMS using Brevo. Input: 'to' (phone number), 'message'.")

    def execute(self, to=None, message=None, payload=None):
         if payload:
             to = payload.get('to')
             message = payload.get('message')
             
         if not to or not message: return "Error: 'to' and 'message' required."
         
         api_key = os.getenv("BREVO_API_KEY")
         if not api_key:
            return f"[MOCK] SMS sent to {to}: {message}\n(Configure BREVO_API_KEY in .env)"

         # Actual API Code would go here (similar to Email)
         return f"[MOCK] SMS sent via Cloud API to {to}: {message}"
