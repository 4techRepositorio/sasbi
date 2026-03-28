import logging

from fastapi import APIRouter, Depends, Request
from fastapi import status as http_status
from fourpro_contracts.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MfaChallengeResponse,
    MfaVerifyRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.db.session import get_db
from fourpro_api.limiter import limiter
from fourpro_api.services.auth_service import AuthService
from fourpro_api.services.password_reset_service import PasswordResetService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_password_service(db: Session = Depends(get_db)) -> PasswordResetService:
    return PasswordResetService(db)


def _refresh_rate_limit() -> str:
    return get_settings().refresh_rate_limit


def _login_rate_limit() -> str:
    return get_settings().login_rate_limit


@router.post(
    "/login",
    response_model=None,
    summary="Login (TICKET-001 + tenant + tenant context + MFA opcional)",
)
@limiter.limit(_login_rate_limit)
def login(
    request: Request,
    body: LoginRequest,
    svc: AuthService = Depends(get_auth_service),
) -> TokenResponse | MfaChallengeResponse:
    result = svc.login(body.email, body.password)
    if isinstance(result, MfaChallengeResponse):
        return result
    logger.info("login_ok", extra={"tenant_id": result.tenant_id})
    return result


@router.post("/mfa/verify", response_model=TokenResponse)
@limiter.limit("20/minute")
def mfa_verify(
    request: Request,
    body: MfaVerifyRequest,
    svc: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return svc.complete_mfa(body.mfa_token, body.code)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
)
@limiter.limit("5/minute")
def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    svc: PasswordResetService = Depends(get_password_service),
) -> ForgotPasswordResponse:
    svc.request_reset(body.email)
    return ForgotPasswordResponse()


@router.post("/reset-password", status_code=http_status.HTTP_200_OK)
@limiter.limit("30/minute")
def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    svc: PasswordResetService = Depends(get_password_service),
) -> dict[str, str]:
    svc.reset_password(body.token, body.new_password)
    return {"detail": "Senha atualizada"}


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(_refresh_rate_limit)
def refresh_tokens(
    request: Request,
    body: RefreshRequest,
    svc: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return svc.refresh(body.refresh_token)
