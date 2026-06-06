import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os

def send_brevo_email(to, subject, body):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to}],
        sender={"name": "QRemind", "email": os.getenv('BREVO_SENDER_EMAIL')},
        subject=subject,
        text_content=body
    )
    
    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        raise Exception(f"Brevo error: {e}")