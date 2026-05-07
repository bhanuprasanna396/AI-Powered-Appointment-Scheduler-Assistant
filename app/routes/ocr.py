from fastapi import APIRouter, HTTPException

from app.models.requests import OCRRequest
from app.models.responses import OCRResponse
from app.services.ocr_service import extract_raw_text

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("", response_model=OCRResponse)
async def ocr_endpoint(payload: OCRRequest) -> OCRResponse:
    try:
        return extract_raw_text(text=payload.text, image_b64=payload.image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"OCR stage failed: {exc}") from exc
