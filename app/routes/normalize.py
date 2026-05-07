from fastapi import APIRouter, HTTPException

from app.models.requests import NormalizeRequest
from app.models.responses import NormalizationResponse
from app.services.normalization_service import normalize_entities

router = APIRouter(prefix="/normalize", tags=["normalize"])


@router.post("", response_model=NormalizationResponse)
async def normalize_endpoint(payload: NormalizeRequest) -> NormalizationResponse:
    try:
        return normalize_entities(payload.date_phrase, payload.time_phrase)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Normalization failed: {exc}") from exc
