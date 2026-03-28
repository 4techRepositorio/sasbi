#!/usr/bin/env python3
"""Remove linhas sintéticas criadas por `seed_e2e_storage_warn.py` (`original_filename` fixo).

Uso:

  export DATABASE_URL=...
  apps/api/.venv/bin/python scripts/cleanup_e2e_storage_seed.py

Opções:
  --dry-run   apenas mostra quantas linhas seriam apagadas
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_API_ROOT = _REPO_ROOT / "apps" / "api"
if not _API_ROOT.is_dir():
    print("Esperada pasta apps/api.", file=sys.stderr)
    sys.exit(1)
sys.path.insert(0, str(_API_ROOT))

os.environ.setdefault("JWT_SECRET", "e2e-cleanup-placeholder-jwt-secret-32chars!")

from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import sessionmaker

from fourpro_api.config import get_settings, reset_settings_cache
from fourpro_api.models.ingestion import FileIngestion

# Manter alinhado com scripts/seed_e2e_storage_warn.py
E2E_SEED_STORAGE_FILENAME = "e2e-seed-storage-warn.bin"


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove seed E2E de quota de armazenamento.")
    parser.add_argument("--dry-run", action="store_true", help="Não apaga, só conta.")
    args = parser.parse_args()

    reset_settings_cache()
    settings = get_settings()
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        stmt_count = select(func.count()).select_from(FileIngestion).where(
            FileIngestion.original_filename == E2E_SEED_STORAGE_FILENAME,
        )
        n = int(db.scalar(stmt_count) or 0)
        if n == 0:
            print("Nenhum registo com original_filename=%r." % E2E_SEED_STORAGE_FILENAME)
            return 0
        if args.dry_run:
            print(f"[dry-run] Seriam removidos {n} registo(s).")
            return 0
        db.execute(
            delete(FileIngestion).where(FileIngestion.original_filename == E2E_SEED_STORAGE_FILENAME),
        )
        db.commit()
        print(f"Removidos {n} registo(s) (%r)." % E2E_SEED_STORAGE_FILENAME)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
