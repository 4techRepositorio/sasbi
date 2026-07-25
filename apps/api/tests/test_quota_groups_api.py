"""API — CRUD de grupos de quota e patch de quotas de membro."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.audit_log import AuditLog
from fourpro_api.models.tenant import TenantMembership
from fourpro_api.repositories.audit_repository import AuditAction
from tests.test_auth import _bind_tenant, _create_user


def _admin_token(client: TestClient, db: Session, email: str) -> tuple[str, uuid.UUID, uuid.UUID]:
    u = _create_user(db, email, "secretpass123")
    tid = _bind_tenant(db, u, role="admin")
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "secretpass123"})
    assert r.status_code == 200
    return r.json()["access_token"], tid, u.id


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.billing
@pytest.mark.rbac
def test_quota_group_crud_happy_path(client: TestClient, db_session: Session) -> None:
    token, _tid, _uid = _admin_token(client, db_session, "qgadmin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/tenant/quota-groups",
        headers=headers,
        json={"name": "Equipa A", "max_storage_mb": 50},
    )
    assert created.status_code == 201
    group = created.json()
    assert group["name"] == "Equipa A"
    assert group["max_storage_mb"] == 50
    gid = group["id"]

    listed = client.get("/api/v1/tenant/quota-groups", headers=headers)
    assert listed.status_code == 200
    assert any(i["id"] == gid for i in listed.json()["items"])

    patched = client.patch(
        f"/api/v1/tenant/quota-groups/{gid}",
        headers=headers,
        json={"max_storage_mb": 80},
    )
    assert patched.status_code == 200
    assert patched.json()["max_storage_mb"] == 80

    empty_patch = client.patch(
        f"/api/v1/tenant/quota-groups/{gid}",
        headers=headers,
        json={},
    )
    assert empty_patch.status_code == 200

    deleted = client.delete(f"/api/v1/tenant/quota-groups/{gid}", headers=headers)
    assert deleted.status_code == 204

    missing = client.get("/api/v1/tenant/quota-groups", headers=headers)
    assert all(i["id"] != gid for i in missing.json()["items"])


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.rbac
def test_quota_groups_forbidden_for_consumer(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "qgcons@example.com", "secretpass123")
    _bind_tenant(db_session, u, role="consumer")
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "qgcons@example.com", "password": "secretpass123"},
    ).json()["access_token"]
    r = client.get(
        "/api/v1/tenant/quota-groups",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.tenant_isolation
@pytest.mark.security
def test_quota_group_cross_tenant_404(client: TestClient, db_session: Session) -> None:
    token_a, _tid_a, _uid_a = _admin_token(client, db_session, "qga@example.com")
    token_b, _tid_b, _uid_b = _admin_token(client, db_session, "qgb@example.com")
    created = client.post(
        "/api/v1/tenant/quota-groups",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "Privado", "max_storage_mb": 10},
    )
    assert created.status_code == 201
    gid = created.json()["id"]

    r = client.patch(
        f"/api/v1/tenant/quota-groups/{gid}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"name": "Hijack"},
    )
    assert r.status_code == 404

    r_del = client.delete(
        f"/api/v1/tenant/quota-groups/{gid}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_del.status_code == 404


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.billing
@pytest.mark.audit
def test_patch_member_storage_quotas(client: TestClient, db_session: Session) -> None:
    token, tid, uid = _admin_token(client, db_session, "qgmem@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    group = client.post(
        "/api/v1/tenant/quota-groups",
        headers=headers,
        json={"name": "G1", "max_storage_mb": 25},
    ).json()

    r = client.patch(
        f"/api/v1/tenant/members/{uid}/quotas",
        headers=headers,
        json={"max_storage_mb": 5, "quota_group_id": group["id"]},
    )
    assert r.status_code == 200
    m = db_session.scalars(
        select(TenantMembership).where(
            TenantMembership.user_id == uid,
            TenantMembership.tenant_id == tid,
        ),
    ).first()
    assert m is not None
    assert m.max_storage_mb == 5
    assert str(m.quota_group_id) == group["id"]

    audits = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.TENANT_MEMBER_QUOTAS_UPDATED),
    ).all()
    assert len(audits) >= 1

    clear = client.patch(
        f"/api/v1/tenant/members/{uid}/quotas",
        headers=headers,
        json={"quota_group_id": None},
    )
    assert clear.status_code == 200
    db_session.refresh(m)
    assert m.quota_group_id is None


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
def test_patch_member_quotas_invalid_group_and_unknown_member(
    client: TestClient, db_session: Session
) -> None:
    token, _tid, uid = _admin_token(client, db_session, "qgbad@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    bad_uuid = client.patch(
        f"/api/v1/tenant/members/{uid}/quotas",
        headers=headers,
        json={"quota_group_id": "not-a-uuid"},
    )
    assert bad_uuid.status_code == 400

    missing_group = client.patch(
        f"/api/v1/tenant/members/{uid}/quotas",
        headers=headers,
        json={"quota_group_id": str(uuid.uuid4())},
    )
    assert missing_group.status_code == 400

    unknown = client.patch(
        f"/api/v1/tenant/members/{uuid.uuid4()}/quotas",
        headers=headers,
        json={"max_storage_mb": 1},
    )
    assert unknown.status_code == 404
