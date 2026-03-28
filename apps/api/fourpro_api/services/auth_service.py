import logging
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from fourpro_contracts.auth import MfaChallengeResponse, TokenResponse
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.core.security import (
    create_access_token,
    create_mfa_pending_token,
    decode_mfa_pending_token,
    hash_otp_code,
    hash_refresh_token,
    new_refresh_token_value,
    verify_password,
)
from fourpro_api.models.tenant import Tenant
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.membership_repository import MembershipRepository
from fourpro_api.repositories.mfa_repository import MfaRepository
from fourpro_api.repositories.refresh_token_repository import RefreshTokenRepository
from fourpro_api.repositories.user_repository import UserRepository
from fourpro_api.services.mail_service import send_plain_email

logger = logging.getLogger(__name__)


def _generate_mfa_numeric_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._refresh = RefreshTokenRepository(db)
        self._members = MembershipRepository(db)
        self._mfa = MfaRepository(db)
        self._audit = AuditRepository(db)

    def login(self, email: str, password: str) -> TokenResponse | MfaChallengeResponse:
        user = self._users.get_by_email(email)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
            )
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
            )

        if user.mfa_enabled:
            code = _generate_mfa_numeric_code()
            exp = datetime.now(tz=UTC) + timedelta(minutes=10)
            self._mfa.upsert_challenge(user.id, hash_otp_code(code), exp)
            mfa_tok = create_mfa_pending_token(user.id)
            logger.info("mfa_challenge_issued", extra={"user_id": str(user.id)})
            send_plain_email(
                to_addr=email,
                subject="4Pro_BI — código de verificação",
                body=(
                    "Utilize o código abaixo para concluir o login (válido por 10 minutos):\n\n"
                    f"{code}\n"
                ),
            )
            m_default = self._members.get_default_membership(user.id)
            self._audit.record(
                action=AuditAction.AUTH_MFA_CHALLENGE_SENT,
                actor_user_id=user.id,
                tenant_id=m_default.tenant_id if m_default else None,
                context={"channel": "email"},
            )
            return MfaChallengeResponse(mfa_token=mfa_tok, expires_in=600)

        return self._issue_tokens_for_user(user)

    def complete_mfa(self, mfa_token: str, code: str) -> TokenResponse:
        user_id = decode_mfa_pending_token(mfa_token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token MFA inválido"
            )

        ch = self._mfa.get_valid(user_id)
        if ch is None or ch.code_hash != hash_otp_code(code.strip()):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código inválido")

        self._mfa.delete(user_id)
        user = self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido")

        return self._issue_tokens_for_user(user)

    def _issue_tokens_for_user(self, user) -> TokenResponse:
        m = self._members.get_default_membership(user.id)
        if m is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nenhum tenant vinculado ao usuário",
            )

        tenant = self._db.get(Tenant, m.tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant inválido")

        access, expires_in = create_access_token(user.id, m.tenant_id, m.role)

        raw_refresh = new_refresh_token_value()
        r_hash = hash_refresh_token(raw_refresh)
        expires_at = datetime.now(tz=UTC) + timedelta(days=get_settings().refresh_token_expire_days)
        self._refresh.create(
            user_id=user.id,
            tenant_id=m.tenant_id,
            token_hash=r_hash,
            expires_at=expires_at,
        )

        self._audit.record(
            action=AuditAction.AUTH_SESSION_ISSUED,
            actor_user_id=user.id,
            tenant_id=m.tenant_id,
            context={"via": "password_or_mfa"},
        )

        return TokenResponse(
            access_token=access,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in=expires_in,
            tenant_id=str(m.tenant_id),
            tenant_name=tenant.name,
            role=m.role,
        )

    def refresh(self, raw_refresh: str) -> TokenResponse:
        r_hash = hash_refresh_token(raw_refresh)
        row = self._refresh.get_valid_by_hash(r_hash)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado",
            )
        if row.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sessão expirada — faça login novamente",
            )

        self._refresh.revoke(row)

        role = self._members.get_role(row.user_id, row.tenant_id)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Membro do tenant não encontrado",
            )

        tenant = self._db.get(Tenant, row.tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant inválido")

        access, expires_in = create_access_token(row.user_id, row.tenant_id, role)

        raw_new = new_refresh_token_value()
        new_hash = hash_refresh_token(raw_new)
        expires_at = datetime.now(tz=UTC) + timedelta(days=get_settings().refresh_token_expire_days)
        self._refresh.create(
            user_id=row.user_id,
            tenant_id=row.tenant_id,
            token_hash=new_hash,
            expires_at=expires_at,
        )

        self._audit.record(
            action=AuditAction.AUTH_TOKEN_REFRESH,
            actor_user_id=row.user_id,
            tenant_id=row.tenant_id,
            context=None,
        )

        return TokenResponse(
            access_token=access,
            refresh_token=raw_new,
            token_type="bearer",
            expires_in=expires_in,
            tenant_id=str(row.tenant_id),
            tenant_name=tenant.name,
            role=role,
        )
