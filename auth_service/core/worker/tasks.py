from typing import Any, Dict, List, Optional

from libs.service.email_service import EmailService
from auth_service.core.worker.config import celery_app


@celery_app.task(bind=True, name="send_email", max_retries=3, default_retry_delay=60)
def send_email_task(self, to_email: str, subject: str, html_content: str) -> None:
    """Send a single email as a background task"""
    try:
        email_service = EmailService()
        email_service.send_email(to_email=to_email, subject=subject, html_content=html_content)
        return f"Email sent to {to_email}"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="send_template_email", max_retries=3, default_retry_delay=60)
def send_template_email_task(
    self, to_email: str, subject: str, template_name: str, template_vars: Dict[str, Any]
) -> None:
    """Send an email using a template as a background task"""
    try:
        email_service = EmailService()
        email_service.send_template_email(
            to_email=to_email, subject=subject, template_name=template_name, template_vars=template_vars
        )
        return f"Template email sent to {to_email}"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="send_welcome_email", max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, to_email: str, first_name: str) -> None:
    """Send welcome email as a background task"""
    try:
        email_service = EmailService()
        email_service.send_welcome_email(to_email=to_email, first_name=first_name)
        return f"Welcome email sent to {to_email}"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="send_password_reset_email", max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(self, to_email: str, first_name: str, reset_token: str) -> None:
    """Send password reset email as a background task"""
    try:
        email_service = EmailService()
        email_service.send_password_reset_email(to_email=to_email, first_name=first_name, reset_token=reset_token)
        return f"Password reset email sent to {to_email}"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="send_password_changed_email", max_retries=3, default_retry_delay=60)
def send_password_changed_email_task(self, to_email: str, first_name: str) -> None:
    """Send password changed notification email as a background task"""
    try:
        email_service = EmailService()
        email_service.send_password_changed_email(to_email=to_email, first_name=first_name)
        return f"Password changed email sent to {to_email}"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="send_bulk_emails", max_retries=3, default_retry_delay=60)
def send_bulk_emails_task(
    self,
    emails: List[str],
    subject: str,
    template_name: str,
    common_template_vars: Dict[str, Any],
    individual_template_vars: Optional[Dict[str, Dict[str, Any]]] = None,
) -> None:
    """Send bulk emails as a background task"""
    try:
        email_service = EmailService()
        email_service.send_bulk_emails(
            emails=emails,
            subject=subject,
            template_name=template_name,
            common_template_vars=common_template_vars,
            individual_template_vars=individual_template_vars,
        )
        return f"Bulk emails sent to {len(emails)} recipients"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)
