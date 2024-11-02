import smtplib
from email.message import EmailMessage
import os
import dotenv

dotenv.load_dotenv()

msg = EmailMessage()
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_HOST')
EMAIL_ADDRESS = os.getenv("EMAIL_HOST_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")