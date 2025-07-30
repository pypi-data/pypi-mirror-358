import smtplib
from email.message import EmailMessage

class SMTPConnector:
    def __init__(self, host, port, username, password, use_tls=True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send_email(self, to_address, subject, content):
        msg = EmailMessage()
        msg["From"] = self.username
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(content)

        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)