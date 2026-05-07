from fastapi import APIRouter, HTTPException

from app.models.requests import ExtractRequest
from app.models.responses import EntityExtractionResponse
from app.services.entity_service import extract_entities

router = APIRouter(prefix="/extract", tags=["extract"])


@router.post("", response_model=EntityExtractionResponse)
async def extract_endpoint(payload: ExtractRequest) -> EntityExtractionResponse:
    try:
        return extract_entities(payload.raw_text)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {exc}") from exc
