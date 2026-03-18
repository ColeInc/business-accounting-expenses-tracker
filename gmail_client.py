import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build


class GmailClient:
    def __init__(self, credentials):
        self.service = build('gmail', 'v1', credentials=credentials)

    def send_email(self, to: str, subject: str, body_html: str, body_text: str = None):
        msg = MIMEMultipart('alternative')
        msg['to'] = to
        msg['subject'] = subject
        if body_text:
            msg.attach(MIMEText(body_text, 'plain'))
        msg.attach(MIMEText(body_html, 'html'))
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return self.service.users().messages().send(
            userId='me', body={'raw': raw}
        ).execute()
