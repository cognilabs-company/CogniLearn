import smtplib
from celery import Celery
from email.message import EmailMessage

from config import (
    MAIL_USERNAME, MAIL_SERVER, MAIL_PASSWORD, MAIL_PORT,
    REDIS_HOST, REDIS_PORT, SMTP_USER, SMTP_PASSWORD
)

# Celery configuration
celery = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)


def get_email_template_dashboard(user_email, code):
    email = EmailMessage()
    email['Subject'] = 'Password Reset Verification Code'
    email['From'] = MAIL_USERNAME
    email['To'] = user_email

    email.set_content(
        f"""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; border: solid 2px rgb(40,169,8); text-align: center; width: 550px; margin: auto; background-color: rgba(144, 238, 144, 0.486);">
            <img src="https://media.licdn.com/dms/image/D560BAQE4NBkII7lrMw/company-logo_200_200/0/1701661109135/cognilabs_software_logo?e=2147483647&v=beta&t=MIQutO18XukzN5MPlywOiM8eJ0YdCZ7VRRXzisS-yMU" alt="Forgot" height="150px" width="150px" style=" border-radius: 50%"/>
                <h1>Cognilabs developers</h1> 
                <h2 style="color: #333;">Hi! 😊</h2>
                <p>You requested to reset your password.</p>
                <p>Please enter the verification code below to reset your password:</p>
                <div style="margin: 20px 0; padding: 15px; background-color: #4CAF50; color: white; font-size: 24px; text-align: center; border-radius: 5px;">
                    {code}
                </div>
                <p>If you didn’t request this password reset, please ignore this email.</p>
            </div>
            """,
        subtype='html'
    )
    return email


@celery.task
def send_mail_for_forget_password(email: str, code: int):
    try:
        email_msg = get_email_template_dashboard(email, code)
        with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(email_msg)
        print(f"Verification email sent to {email}")
    except smtplib.SMTPException as e:
        print(f"Failed to send email to {email}. SMTP error: {str(e)}")
    except Exception as e:
        print(f"Failed to send email to {email}. Error: {str(e)}")
