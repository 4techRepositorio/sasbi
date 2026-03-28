import logging
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.core.security import hash_password, hash_refresh_token
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.membership_repository import MembershipRepository
from fourpro_api.repositories.password_reset_repository import PasswordResetRepository
from fourpro_api.repositories.refresh_token_repository import RefreshTokenRepository
from fourpro_api.repositories.user_repository import UserRepository
from fourpro_api.services.mail_service import send_plain_email

logger = logging.getLogger(__name__)


class PasswordResetService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._tokens = PasswordResetRepository(db)
        self._refresh = RefreshTokenRepository(db)
        self._members = MembershipRepository(db)
        self._audit = AuditRepository(db)

    def request_reset(self, email: str) -> None:
        user = self._users.get_by_email(email)
        if user is None:
            return
        raw = secrets.token_urlsafe(32)
        th = hash_refresh_token(raw)
        exp = datetime.now(tz=UTC) + timedelta(hours=1)
        self._tokens.create(user_id=user.id, token_hash=th, expires_at=exp)
        settings = get_settings()
        link = f"{settings.app_public_url.rstrip('/')}/login"
        reset_page = f"{settings.app_public_url.rstrip('/')}/reset-password?token={raw}"
        body = (
            "Pedido de redefinição de senha no 4Pro_BI.\n\n"
            f"Abrir na aplicação (recomendado):\n{reset_page}\n\n"
            f"Ou copie o token e use no ecrã «Redefinir com token»:\n{raw}\n\n"
            f"Login: {link}\n\n"
            "Se não foi você, ignore este email."
        )
        send_plain_email(
            to_addr=email,
            subject="4Pro_BI — redefinição de senha",
            body=body,
        )
        m = self._members.get_default_membership(user.id)
        self._audit.record(
            action=AuditAction.AUTH_PASSWORD_RESET_REQUESTED,
            actor_user_id=user.id,
            tenant_id=m.tenant_id if m else None,
            context=None,
        )
        logger.info("password_reset_email_sent", extra={"user_id": str(user.id)})

    def reset_password(self, raw_token: str, new_password: str) -> None:
        th = hash_refresh_token(raw_token)
        row = self._tokens.get_valid_by_hash(th)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou expirado",
            )
        user = self._users.get_by_id(row.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inválido")

        self._users.update_password_hash(user, hash_password(new_password))
        self._tokens.mark_used(row)
        self._refresh.revoke_all_for_user(user.id)
        m = self._members.get_default_membership(user.id)
        self._audit.record(
            action=AuditAction.AUTH_PASSWORD_RESET_COMPLETED,
            actor_user_id=user.id,
            tenant_id=m.tenant_id if m else None,
            context=None,
        )
        logger.info("password_reset_ok", extra={"user_id": str(user.id)})
