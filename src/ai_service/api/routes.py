from fastapi import APIRouter, HTTPException

from ai_service.config.settings import settings
from ai_service.services.ai_service import AIService
from ai_service.utils.logging import configure_logging

router = APIRouter()
logger = configure_logging()
ai_service = AIService(logger)


@router.get("/")
def root() -> dict[str, str]:
    return {
        "message": "AI Service is running",
        "version": settings.APP_VERSION,
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/version")
def version() -> dict[str, str]:
    return {"version": settings.APP_VERSION}


@router.post("/classify")
def classify(text: str) -> dict[str, str]:
    try:
        return ai_service.classify(text)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
