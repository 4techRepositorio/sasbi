from typing import Literal, TypeAlias

from pydantic import BaseModel, EmailStr, Field

TokenTypeBearer: TypeAlias = Literal["bearer"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10, max_length=2048)


class TokenResponse(BaseModel):
    mfa_required: Literal[False] = False
    access_token: str
    refresh_token: str
    token_type: TokenTypeBearer = "bearer"
    expires_in: int
    tenant_id: str | None = None
    tenant_name: str | None = None
    role: str | None = None


class MfaChallengeResponse(BaseModel):
    mfa_required: Literal[True] = True
    mfa_token: str
    expires_in: int = 600


class MfaVerifyRequest(BaseModel):
    mfa_token: str
    code: str = Field(min_length=4, max_length=12)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    detail: str = "Se existir uma conta associada a este email, enviaremos instruções."


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=16, max_length=2048)
    new_password: str = Field(min_length=8, max_length=256)
