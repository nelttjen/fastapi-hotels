import logging
import smtplib

from src.config import google_smtp_settings, DOMAIN, CONNECTION_PROTOCOL
from email.message import EmailMessage
from src.celery.celery import celery_app
from src.auth.models import CodeTypes
from src.utils import assert_never

logger = logging.getLogger('all')


class MailTemplate:
    def __init__(self, email: str, code: str, code_type: CodeTypes):
        self.email = email
        self.code = code
        self.code_type = code_type

    def get_email(self) -> EmailMessage:
        match self.code_type:
            case CodeTypes.ACTIVATION:
                return self.prepare_activation_email()
            case CodeTypes.RECOVERY:
                return self.prepare_recovery_email()
            case _:
                assert_never(self.code_type)

    def prepare_activation_email(self) -> EmailMessage:
        message = EmailMessage()
        message['Subject'] = 'Welcome to booking service! Activate your account'
        message['From'] = google_smtp_settings.SMTP_USER
        message['To'] = self.email

        activation_url = f'{CONNECTION_PROTOCOL}://{DOMAIN}/auth/activate?code={self.code}'

        message.set_content(
            f"""
                <h1> Welcome to booking service! </h1>
                <p> Please click the link below to activate your account: 
                <a href="{activation_url}">{activation_url}</a></p>
                """,
            subtype='html',
        )
        return message

    def prepare_recovery_email(self) -> EmailMessage:
        message = EmailMessage()
        message['Subject'] = 'Restore your password on the booking service!'
        message['From'] = google_smtp_settings.SMTP_USER
        message['To'] = self.email

        recovery_url = f'{CONNECTION_PROTOCOL}://{DOMAIN}/auth/recovery?code={self.code}'

        message.set_content(
            f"""
                    <h1> Hello! You have requested a link to restore your account on the bookings service!</h1>
                    <p> Please click the link below to restore your account: 
                    <a href="{recovery_url}">{recovery_url}</a></p>
                    """,
            subtype='html',
        )
        return message


def send_email(message: EmailMessage) -> None:
    try:
        with smtplib.SMTP_SSL(google_smtp_settings.SMTP_HOST, google_smtp_settings.SMTP_PORT) as server:
            server.login(google_smtp_settings.SMTP_USER, google_smtp_settings.SMTP_PASSWORD)
            server.sendmail(message['From'], [message['To']], message.as_string())
    except Exception as e:
        logger.error(e)
    pass


@celery_app.task
def send_recovery_email(email, code):
    logger.info('Sending recovery email to %s' % email)
    message = MailTemplate(email, code, CodeTypes.RECOVERY).get_email()
    send_email(message)


@celery_app.task
def send_activation_email(email, code):
    logger.info('Sending activation email to %s' % email)
    message = MailTemplate(email, code, CodeTypes.ACTIVATION).get_email()
    send_email(message)
