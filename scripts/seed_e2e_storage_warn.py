#!/usr/bin/env python3
"""Insere uma linha sintética em `file_ingestions` para elevar o uso do tenant a ~91,5 % do plano.

Objetivo: permitir o teste Playwright opcional com `E2E_EXPECT_STORAGE_WARN=1` (`data-storage-warn`).

Uso (na raiz do monorepo, com as mesmas variáveis que a API):

  export DATABASE_URL=postgresql+psycopg://...
  export JWT_SECRET=...   # mínimo 32 caracteres se o Settings o exigir
  apps/api/.venv/bin/python scripts/seed_e2e_storage_warn.py

Variáveis opcionais:
  SEED_TENANT_SLUG   (default: demo)
  SEED_UPLOAD_USER_EMAIL — `uploaded_by_user_id` na linha (default: admin@local.dev)

Não cria ficheiro em disco: só metadata na BD (o somatório de quotas usa `size_bytes`).

Reverter: `scripts/cleanup_e2e_storage_seed.py` ou `./scripts/run-cleanup-e2e-storage-warn.sh`.
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_API_ROOT = _REPO_ROOT / "apps" / "api"
if not _API_ROOT.is_dir():
    print("Esperada pasta apps/api a partir da raiz do repositório.", file=sys.stderr)
    sys.exit(1)
sys.path.insert(0, str(_API_ROOT))

os.environ.setdefault("JWT_SECRET", "e2e-seed-placeholder-jwt-secret-32chars!!")

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from fourpro_api.config import get_settings, reset_settings_cache
from fourpro_api.models.ingestion import FileIngestion
from fourpro_api.models.plan import Plan
from fourpro_api.models.subscription import TenantSubscription
from fourpro_api.models.tenant import Tenant
from fourpro_api.models.user import User

E2E_SEED_STORAGE_FILENAME = "e2e-seed-storage-warn.bin"


def _used_bytes(db: Session, tenant_id: uuid.UUID) -> int:
    stmt = select(func.coalesce(func.sum(FileIngestion.size_bytes), 0)).where(
        FileIngestion.tenant_id == tenant_id,
    )
    return int(db.scalar(stmt) or 0)


def main() -> int:
    reset_settings_cache()
    settings = get_settings()
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        slug = os.environ.get("SEED_TENANT_SLUG", "demo").strip() or "demo"
        tenant = db.scalars(select(Tenant).where(Tenant.slug == slug)).first()
        if tenant is None:
            print(f"Tenant com slug={slug!r} não encontrado.", file=sys.stderr)
            return 1

        sub = db.scalars(
            select(TenantSubscription).where(TenantSubscription.tenant_id == tenant.id),
        ).first()
        if sub is None:
            print("Tenant sem subscrição / plano.", file=sys.stderr)
            return 1

        plan = db.get(Plan, sub.plan_id)
        if plan is None or plan.max_storage_mb <= 0:
            print("Plano inválido ou max_storage_mb = 0.", file=sys.stderr)
            return 1

        cap = plan.max_storage_mb * 1024 * 1024
        used = _used_bytes(db, tenant.id)
        target = int(cap * 0.915)
        delta = target - used
        if delta <= 0:
            print(f"Uso actual {used} bytes já ≥ 91,5 % do tecto {cap}. Nada a inserir.")
            return 0

        email = os.environ.get("SEED_UPLOAD_USER_EMAIL", "admin@local.dev").strip()
        user = db.scalars(select(User).where(User.email == email)).first()
        uid = user.id if user else None

        now = datetime.now(tz=UTC)
        row = FileIngestion(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            original_filename=E2E_SEED_STORAGE_FILENAME,
            storage_path="/tmp/e2e-seed-storage-warn-placeholder",
            content_type="application/octet-stream",
            size_bytes=delta,
            status="processed",
            uploaded_by_user_id=uid,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        db.commit()
        new_used = used + delta
        pct = 100.0 * new_used / cap if cap else 0
        print(
            f"Inserido registo sintético: +{delta} B → uso tenant {new_used} B "
            f"({pct:.1f} % de {plan.max_storage_mb} MB).",
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
