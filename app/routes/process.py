from fastapi import APIRouter, HTTPException

from app.models.requests import ProcessRequest
from app.models.responses import ProcessResponse
from app.services.pipeline_service import run_pipeline

router = APIRouter(prefix="/process", tags=["process"])


@router.post("", response_model=ProcessResponse)
async def process_endpoint(payload: ProcessRequest) -> ProcessResponse:
    try:
        return run_pipeline(text=payload.text, image_b64=payload.image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc
