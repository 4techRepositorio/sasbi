from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness")
def health() -> dict[str, str]:
    return {"status": "ok"}
