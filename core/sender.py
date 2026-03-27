import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Callable, Optional

class EmailSender:
    def __init__(self, sender_email: str, app_password: str, smtp_server="smtp.gmail.com", smtp_port=465):
        self.sender = sender_email
        self.password = app_password
        self.server = smtp_server
        self.port = smtp_port

    def send(self, to: str, subject: str, body: str, status_callback: Optional[Callable[[str, bool, str], None]] = None):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            with smtplib.SMTP_SSL(self.server, self.port) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            if status_callback:
                status_callback(to, True, "Успешно отправлено")
            return True
        except Exception as e:
            if status_callback:
                status_callback(to, False, str(e))
            return False

    def send_batch(self, emails: List[Dict], delay_min: float, delay_max: float,
                   status_callback: Callable[[str, bool, str], None],
                   progress_callback: Optional[Callable[[int, int], None]] = None):
        total = len(emails)
        for i, email in enumerate(emails):
            self.send(email['to'], email['subject'], email['body'], status_callback)
            if progress_callback:
                progress_callback(i+1, total)
            if i < total - 1:
                delay = random.uniform(delay_min, delay_max)
                time.sleep(delay)