"""Email sending utilities for VaultX.

This module provides a simple `send_password_reset_email` implementation that
will attempt to send via SMTP when SMTP settings are provided; otherwise it
logs the reset link to the console for local development.
"""
import smtplib
from email.message import EmailMessage
from typing import Optional
from urllib.parse import urlencode

from app.config import settings


def _build_reset_link(token: str) -> str:
    params = urlencode({"token": token})
    return f"{settings.FRONTEND_URL.rstrip('/')}" + "/reset-password?" + params


def send_password_reset_email(to_email: str, token: str, user_name: Optional[str] = None) -> bool:
    link = _build_reset_link(token)
    subject = "VaultX Password Reset"
    body = f"Hello {user_name or ''},\n\nTo reset your VaultX password click the link below:\n{link}\n\nIf you didn't request this, you can ignore this message."

    # Try SMTP if settings are present
    smtp_host = getattr(settings, "SMTP_HOST", None)
    smtp_port = getattr(settings, "SMTP_PORT", 587)
    smtp_user = getattr(settings, "SMTP_USER", None)
    smtp_pass = getattr(settings, "SMTP_PASS", None)

    if smtp_host and smtp_user and smtp_pass:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = getattr(settings, "SMTP_FROM", f"no-reply@{settings.FRONTEND_URL}")
        msg["To"] = to_email
        msg.set_content(body)
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
                s.starttls()
                s.login(smtp_user, smtp_pass)
                s.send_message(msg)
            return True
        except Exception:
            # Fall through to console fallback
            pass

    # Console fallback for local development
    print("[email_service] Password reset link for", to_email)
    print(link)
    return False
