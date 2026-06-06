import resend
import os

def send_resend_email(to, subject, body):
    resend.api_key = os.getenv('RESEND_API_KEY')
    
    params = {
        "from": "QRemind <onboarding@resend.dev>",
        "to": [to],
        "subject": subject,
        "text": body
    }
    
    return resend.Emails.send(params)