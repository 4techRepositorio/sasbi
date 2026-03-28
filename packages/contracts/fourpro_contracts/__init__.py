"""Contratos Pydantic compartilhados."""

from fourpro_contracts.billing import MeContextResponse, PlanSummary, StorageContext
from fourpro_contracts.dataset import DatasetItem, PaginatedDatasetList
from fourpro_contracts.ingestion import (
    IngestionItem,
    IngestionLifecycleStatus,
    UploadCreatedResponse,
)
from fourpro_contracts.tenant import (
    MemberStorageQuotaPatch,
    TenantAuditLogItem,
    TenantAuditLogListResponse,
    TenantMemberItem,
    TenantMemberListResponse,
    TenantQuotaGroupCreate,
    TenantQuotaGroupItem,
    TenantQuotaGroupListResponse,
    TenantQuotaGroupPatch,
)

from fourpro_contracts.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MfaChallengeResponse,
    MfaVerifyRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    TokenTypeBearer,
)

__all__ = [
    "MeContextResponse",
    "PlanSummary",
    "StorageContext",
    "DatasetItem",
    "PaginatedDatasetList",
    "IngestionItem",
    "IngestionLifecycleStatus",
    "UploadCreatedResponse",
    "TenantAuditLogItem",
    "TenantAuditLogListResponse",
    "TenantMemberItem",
    "TenantMemberListResponse",
    "TenantQuotaGroupItem",
    "TenantQuotaGroupListResponse",
    "TenantQuotaGroupCreate",
    "TenantQuotaGroupPatch",
    "MemberStorageQuotaPatch",
    "LoginRequest",
    "RefreshRequest",
    "TokenResponse",
    "TokenTypeBearer",
    "MfaChallengeResponse",
    "MfaVerifyRequest",
    "ForgotPasswordRequest",
    "ForgotPasswordResponse",
    "ResetPasswordRequest",
]
