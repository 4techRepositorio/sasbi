import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from fourpro_api.config import get_settings
from fourpro_api.core.principal import Principal

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, password_hash: str) -> bool:
    return pwd_context.verify(plain, password_hash)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_otp_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def new_refresh_token_value() -> str:
    return secrets.token_urlsafe(48)


def create_access_token(user_id: UUID, tenant_id: UUID, role: str) -> tuple[str, int]:
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(tz=UTC) + expires_delta
    payload = {
        "sub": str(user_id),
        "tid": str(tenant_id),
        "role": role,
        "exp": expire,
        "typ": "access",
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def decode_access_token(token: str) -> Principal | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("typ") != "access":
            return None
        sub = payload.get("sub")
        tid = payload.get("tid")
        role = payload.get("role")
        if not sub or not tid or not role:
            return None
        return Principal(user_id=UUID(sub), tenant_id=UUID(tid), role=str(role))
    except (JWTError, ValueError):
        return None


def create_mfa_pending_token(user_id: UUID) -> str:
    settings = get_settings()
    expire = datetime.now(tz=UTC) + timedelta(minutes=10)
    payload = {"sub": str(user_id), "exp": expire, "typ": "mfa_pending"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_mfa_pending_token(token: str) -> UUID | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("typ") != "mfa_pending":
            return None
        sub = payload.get("sub")
        if not sub:
            return None
        return UUID(sub)
    except (JWTError, ValueError):
        return None
