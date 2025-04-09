import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import jinja2

from libs import settings


class EmailService:
    def __init__(self):
        self.host = settings.MAIL_HOST
        self.port = settings.MAIL_PORT
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.from_email = settings.MAIL_FROM
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("auth_service/core/templates"),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )

    def send_email(self, to_email: str, subject: str, html_content: str) -> None:
        """Send email with HTML content"""
        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))
        smtp = smtplib.SMTP(host=self.host, port=self.port)
        smtp.starttls()
        smtp.login(self.username, self.password)
        smtp.send_message(message)
        smtp.quit()

    def send_template_email(
        self, to_email: str, subject: str, template_name: str, template_vars: Dict[str, Any]
    ) -> None:
        """Send email using a template"""
        template = self.template_env.get_template(template_name)
        html_content = template.render(**template_vars)
        self.send_email(to_email, subject, html_content)

    def send_welcome_email(self, to_email: str, first_name: str) -> None:
        """Send welcome email to new users"""
        template_vars = {"first_name": first_name, "login_url": f"{settings.BASE_URL}/login"}
        self.send_template_email(
            to_email=to_email,
            subject="Welcome to Our Platform",
            template_name="welcome.html",
            template_vars=template_vars,
        )

    def send_password_reset_email(self, to_email: str, first_name: str, reset_token: str) -> None:
        """Send password reset email"""
        template_vars = {"first_name": first_name, "reset_token": reset_token, "current_year": datetime.now().year}
        self.send_template_email(
            to_email=to_email,
            subject="Password Reset Request",
            template_name="reset-password.html",
            template_vars=template_vars,
        )

    def send_password_changed_email(self, to_email: str, first_name: str) -> None:
        """Send notification when password has been changed"""
        template_vars = {"first_name": first_name}
        self.send_template_email(
            to_email=to_email,
            subject="Your Password Has Been Changed",
            template_name="password-changed.html",
            template_vars=template_vars,
        )

    def send_bulk_emails(
        self,
        emails: List[str],
        subject: str,
        template_name: str,
        common_template_vars: Dict[str, Any],
        individual_template_vars: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        """Send bulk emails using a template"""
        if individual_template_vars is None:
            individual_template_vars = {}
        for email in emails:
            template_vars = common_template_vars.copy()
            if email in individual_template_vars:
                template_vars.update(individual_template_vars[email])
            self.send_template_email(
                to_email=email, subject=subject, template_name=template_name, template_vars=template_vars
            )
