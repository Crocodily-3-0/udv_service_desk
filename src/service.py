import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config import MAIL_LOGIN, MAIL_PWD


async def check_dict(result):
    if result:
        return dict(result)
    return None


async def send_mail(to_addr: str, subject: str, msg: str):
    multipart_msg = MIMEMultipart()
    multipart_msg['From'] = MAIL_LOGIN
    multipart_msg['To'] = to_addr
    multipart_msg['Subject'] = subject
    multipart_msg.attach(MIMEText(msg, 'plain'))

    smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_obj.starttls()
    smtp_obj.login(MAIL_LOGIN, MAIL_PWD)
    smtp_obj.send_message(multipart_msg)
    smtp_obj.quit()
    print("письмо отправлено")

if __name__ == '__main__':
    print("Hello")
    asyncio.run(send_mail("puzanovim@yandex.ru", "HELLO", "Hello Hello"))
