from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from fourpro_api.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness (ligação à base de dados)")
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
