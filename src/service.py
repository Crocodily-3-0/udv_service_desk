import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pydantic import BaseModel

from src.config import MAIL_LOGIN, MAIL_PWD


async def check_dict(result):
    if result:
        return dict(result)
    return None


class Email(BaseModel):
    recipient: str
    title: str
    message: str


async def send_mail(email: Email):
    multipart_msg = MIMEMultipart()
    multipart_msg['From'] = MAIL_LOGIN
    multipart_msg['To'] = email.recipient
    multipart_msg['Subject'] = email.title
    multipart_msg.attach(MIMEText(email.message, 'plain'))

    smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_obj.starttls()
    smtp_obj.login(MAIL_LOGIN, MAIL_PWD)
    smtp_obj.send_message(multipart_msg)
    smtp_obj.quit()
    print(f"письмо отправлено {email.recipient}")
