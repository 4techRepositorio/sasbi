import logging
import smtplib
import ssl
from email.message import EmailMessage

from fourpro_api.config import get_settings

logger = logging.getLogger(__name__)


def send_plain_email(*, to_addr: str, subject: str, body: str) -> None:
    """Envia email texto. Sem SMTP configurado, regista apenas (dev)."""
    settings = get_settings()
    host = (settings.smtp_host or "").strip()
    if not host:
        logger.warning(
            "email_not_configured",
            extra={"to": to_addr, "subject": subject, "preview": body[:280]},
        )
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_addr
    msg.set_content(body)

    if settings.smtp_use_tls:
        context = ssl.create_default_context()
        with smtplib.SMTP(host=host, port=settings.smtp_port) as server:
            server.starttls(context=context)
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password or "")
            server.send_message(msg)
    else:
        with smtplib.SMTP(host=host, port=settings.smtp_port) as server:
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password or "")
            server.send_message(msg)

    logger.info("email_sent", extra={"to": to_addr, "subject": subject})
