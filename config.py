import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
SECRET = os.environ.get('SECRET')

MAIL_USERNAME = 'Cognilabs Developers Team'
MAIL_FROM = 'bek0010311@gmail.com'
MAIL_PORT =465
MAIL_SERVER ='smtp.gmail.com'
MAIL_PASSWORD ='ukokmhdrbiiyerxj'
RESET_PASSWORD_REDIRECT_URL: str = 'reset-password'
RESET_PASSWORD_EXPIRY_MINUTES: int = 60 * 12
REDIS_HOST ='localhost'
REDIS_PORT=6379
SMTP_USER = 'bek0010311@gmail.com'
SMTP_PASSWORD ='ukokmhdrbiiyerxj'

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET_KEY = os.environ.get('GOOGLE_CLIENT_SECRET_KEY')
GOOGLE_REDIRECT_URL = os.environ.get('GOOGLE_REDIRECT_URL')

