"""Unitários — mail service (dev log vs SMTP mock)."""

from unittest.mock import MagicMock, patch

import pytest

from fourpro_api.config import reset_settings_cache
from fourpro_api.services.mail_service import send_plain_email


@pytest.mark.unit
def test_send_plain_email_without_smtp_logs_only(caplog, monkeypatch) -> None:
    monkeypatch.delenv("SMTP_HOST", raising=False)
    reset_settings_cache()
    with caplog.at_level("WARNING"):
        send_plain_email(to_addr="a@example.com", subject="Hi", body="body text")
    assert any(
        "email_not_configured" in (getattr(r, "message", "") or "")
        or getattr(r, "msg", "") == "email_not_configured"
        for r in caplog.records
    )


@pytest.mark.unit
def test_send_plain_email_with_tls_smtp(monkeypatch) -> None:
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "user")
    monkeypatch.setenv("SMTP_PASSWORD", "pass")
    monkeypatch.setenv("SMTP_FROM", "noreply@example.com")
    monkeypatch.setenv("SMTP_USE_TLS", "true")
    reset_settings_cache()

    server = MagicMock()
    server.__enter__ = MagicMock(return_value=server)
    server.__exit__ = MagicMock(return_value=False)

    with patch("fourpro_api.services.mail_service.smtplib.SMTP", return_value=server) as smtp:
        send_plain_email(to_addr="to@example.com", subject="Subj", body="Hello")
        smtp.assert_called_once()
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("user", "pass")
        server.send_message.assert_called_once()

    reset_settings_cache()


@pytest.mark.unit
def test_send_plain_email_without_tls(monkeypatch) -> None:
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "25")
    monkeypatch.setenv("SMTP_USE_TLS", "false")
    monkeypatch.delenv("SMTP_USER", raising=False)
    reset_settings_cache()

    server = MagicMock()
    server.__enter__ = MagicMock(return_value=server)
    server.__exit__ = MagicMock(return_value=False)

    with patch("fourpro_api.services.mail_service.smtplib.SMTP", return_value=server):
        send_plain_email(to_addr="to@example.com", subject="Subj", body="Hello")
        server.starttls.assert_not_called()
        server.send_message.assert_called_once()

    reset_settings_cache()
