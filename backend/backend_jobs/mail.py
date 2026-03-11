import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

SMTP_HOST  = 'localhost'
SMTP_PORT  = 1025
FROM_EMAIL = 'dnyaneshwarirmahajan@gmail.com'


def send_email(to_email, subject, body, attachment=None, filename=None):
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email

    msg.attach(MIMEText(body, 'html'))

    if attachment and filename:
        part = MIMEBase('text', 'csv')                          
        part.set_payload(attachment.encode('utf-8'))
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')  
        part.add_header('Content-Type', 'text/csv; charset=utf-8')
        msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")